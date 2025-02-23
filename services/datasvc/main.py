import uuid
from decimal import Decimal
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import text

from . import models, schema
from .database import engine, get_db
from .utils import calculate_spherical_distance

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="False Positive")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


def flip_coordinates(geojson):
    """Flip coordinates in a GeoJSON object."""
    if not geojson or not isinstance(geojson, dict):
        return geojson

    if geojson.get('type') == 'MultiPolygon':
        # MultiPolygon structure: [ [[[x, y], [x, y], ...]], [[[x, y], ...]], ... ]
        for polygon in geojson.get('coordinates', []):
            for ring in polygon:
                for coord in ring:
                    coord[0], coord[1] = coord[1], coord[0]
    elif geojson.get('type') == 'Polygon':
        # Polygon structure: [[[x, y], [x, y], ...]]
        for ring in geojson.get('coordinates', []):
            for coord in ring:
                coord[0], coord[1] = coord[1], coord[0]
    elif geojson.get('type') == 'Point':
        # Point structure: [x, y]
        coords = geojson.get('coordinates', [])
        if len(coords) >= 2:
            coords[0], coords[1] = coords[1], coords[0]
    
    return geojson


# Node endpoints
@app.get("/nodes", response_model=list[schema.Node])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Node).offset(skip).limit(limit).all()


@app.get("/nodes/{node_id}", response_model=schema.Node)
def read_node(node_id: UUID, db: Session = Depends(get_db)):
    db_node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node


@app.get("/routes/{start_node_id}/{end_node_id}", response_model=schema.ShortestPathResponse)
def get_shortest_path(start_node_id: UUID, end_node_id: UUID, db: Session = Depends(get_db)):
    # First verify both nodes exist
    start_node = db.query(models.Node).filter(models.Node.id == start_node_id).first()
    end_node = db.query(models.Node).filter(models.Node.id == end_node_id).first()

    if not start_node or not end_node:
        raise HTTPException(status_code=404, detail="Start or end node not found")

    # Get the shortest path using pgr_dijkstra
    setup_query = text(
        """
        -- Create temporary tables for our node mapping
        CREATE TEMPORARY TABLE IF NOT EXISTS temp_node_mapping (
            id uuid PRIMARY KEY,
            node_number bigint
        );
        
        INSERT INTO temp_node_mapping (id, node_number)
        SELECT id, ROW_NUMBER() OVER () as node_number
        FROM false_positive.nodes;
        
        -- Create temporary table for edge mapping
        CREATE TEMPORARY TABLE IF NOT EXISTS temp_edge_mapping (
            id bigint,
            source bigint,
            target bigint,
            cost float
        );
        
        INSERT INTO temp_edge_mapping (id, source, target, cost)
        SELECT 
            ROW_NUMBER() OVER ()::bigint as id,
            src.node_number as source,
            tgt.node_number as target,
            e.distance as cost
        FROM false_positive.edges e
        JOIN temp_node_mapping src ON e.source_node_id = src.id
        JOIN temp_node_mapping tgt ON e.target_node_id = tgt.id;
    """
    )

    path_query = text(
        """
        WITH path AS (
            SELECT 
                node as node_number,
                edge,
                agg_cost as distance_from_start
            FROM pgr_dijkstra(
                'SELECT id, source, target, cost FROM temp_edge_mapping',
                (SELECT node_number FROM temp_node_mapping WHERE id = :start),
                (SELECT node_number FROM temp_node_mapping WHERE id = :end)
            )
        )
        SELECT 
            n.id,
            n.node_type,
            n.display_name,
            n.latitude,
            n.longitude,
            COALESCE(p.distance_from_start, 0) as distance_from_start,
            -- Dam specific fields
            d.max_volume as dam_max_volume,
            d.description as dam_description,
            d.municipality as dam_municipality,
            d.owner as dam_owner,
            d.operator as dam_operator,
            -- Place specific fields
            pl.population as place_population,
            pl.consumption_per_capita as place_consumption_per_capita,
            pl.water_price as place_water_price,
            pl.non_dam_incoming_flow as place_non_dam_incoming_flow,
            pl.radius as place_radius,
            pl.municipality as place_municipality,
            -- Junction specific fields
            j.max_flow_rate as junction_max_flow_rate,
            j.current_flow_rate as junction_current_flow_rate,
            j.length as junction_length,
            j.source_node_id as junction_source_node_id,
            j.target_node_id as junction_target_node_id
        FROM path p
        JOIN temp_node_mapping ni ON p.node_number = ni.node_number
        JOIN false_positive.nodes n ON n.id = ni.id
        LEFT JOIN false_positive.dams d ON d.id = n.id
        LEFT JOIN false_positive.places pl ON pl.id = n.id
        LEFT JOIN false_positive.junctions j ON j.id = n.id
        ORDER BY p.distance_from_start;
    """
    )

    cleanup_query = text(
        """
        DROP TABLE IF EXISTS temp_node_mapping;
        DROP TABLE IF EXISTS temp_edge_mapping;
    """
    )

    try:
        # Setup temporary tables
        db.execute(setup_query)

        # Get the path
        result = db.execute(
            path_query, {"start": str(start_node_id), "end": str(end_node_id)}
        ).fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No path found between the specified nodes")

        # Convert the results to our response format
        path_nodes = []
        for row in result:
            node_data = {
                "id": row.id,
                "node_type": row.node_type,
                "display_name": row.display_name,
                "latitude": float(row.latitude),
                "longitude": float(row.longitude),
                "distance_from_start": float(row.distance_from_start),
            }

            # Add type-specific data
            if row.node_type == "dam" and row.dam_max_volume is not None:
                node_data["dam_data"] = {
                    "max_volume": float(row.dam_max_volume),
                    "description": row.dam_description,
                    "municipality": row.dam_municipality,
                    "owner": row.dam_owner,
                    "operator": row.dam_operator,
                }
            elif row.node_type == "place" and row.place_population is not None:
                node_data["place_data"] = {
                    "population": row.place_population,
                    "consumption_per_capita": float(row.place_consumption_per_capita),
                    "water_price": float(row.place_water_price),
                    "non_dam_incoming_flow": float(row.place_non_dam_incoming_flow),
                    "radius": float(row.place_radius),
                    "municipality": row.place_municipality,
                }
            elif row.node_type == "junction" and row.junction_max_flow_rate is not None:
                node_data["junction_data"] = {
                    "max_flow_rate": float(row.junction_max_flow_rate),
                    "current_flow_rate": (
                        float(row.junction_current_flow_rate)
                        if row.junction_current_flow_rate is not None
                        else None
                    ),
                    "length": float(row.junction_length),
                    "source_node_id": row.junction_source_node_id,
                    "target_node_id": row.junction_target_node_id,
                }

            path_nodes.append(node_data)

        # Total distance is the distance_from_start of the last node
        total_distance = float(path_nodes[-1]["distance_from_start"]) if path_nodes else 0.0

        return {"path": path_nodes, "total_distance": total_distance}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating shortest path: {str(e)}")
    finally:
        # Clean up temporary tables
        db.execute(cleanup_query)
        db.commit()


# Dam endpoints
@app.post("/dams", response_model=schema.Dam)
def create_dam(dam: schema.DamCreate, db: Session = Depends(get_db)):
    try:
        # Create node first
        node_id = uuid.uuid4()
        db_node = models.Node(
            id=node_id,
            display_name=dam.display_name,
            latitude=dam.latitude,
            longitude=dam.longitude,
            node_type="dam",
        )
        db.add(db_node)
        db.flush()  # Ensure the node is created before the dam

        # Create dam with same ID
        db_dam = models.Dam(
            id=node_id,
            border_geometry=dam.border_geometry,
            max_volume=dam.max_volume,
            description=dam.description,
            municipality=dam.municipality,
            owner=dam.owner,
            owner_contact=dam.owner_contact,
            operator=dam.operator,
            operator_contact=dam.operator_contact,
        )

        # Add places if any
        if dam.place_ids:
            places = db.query(models.Place).filter(models.Place.id.in_(dam.place_ids)).all()
            db_dam.places = places

        db.add(db_dam)

        # Commit both records in a single transaction
        db.commit()
        db.refresh(db_dam)
        db.refresh(db_node)

        # Return combined dam info
        return {
            **db_dam.__dict__,
            "border_geometry": flip_coordinates(db_dam.border_geometry),
            "display_name": db_node.display_name,
            "latitude": db_node.latitude,
            "longitude": db_node.longitude,
            "created_at": db_node.created_at,
            "updated_at": db_node.updated_at,
            "places": [
                {"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name}
                for place in db_dam.places
            ],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dams", response_model=list[schema.Dam])
def read_dams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Get dams with their nodes
    dams = (
        db.query(models.Dam, models.Node)
        .join(models.Node, models.Dam.id == models.Node.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for dam, node in dams:
        # Get last 2 measurements for this dam
        measurements = (
            db.query(models.DamBulletinMeasurement)
            .filter(models.DamBulletinMeasurement.dam_id == dam.id)
            .order_by(models.DamBulletinMeasurement.timestamp.desc())
            .limit(2)
            .all()
        )
        # Reverse to get chronological order
        measurements.reverse()

        # Combine dam info with node info and measurements
        dam_dict = {
            **dam.__dict__,
            "border_geometry": flip_coordinates(dam.border_geometry),
            "display_name": node.display_name,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
            "places": [
                {"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name}
                for place in dam.places
            ],
            "measurements": measurements,
        }
        result.append(dam_dict)

    return result


@app.get("/dams/{dam_id}", response_model=schema.Dam)
def read_dam(dam_id: UUID, db: Session = Depends(get_db)):
    # Get dam with its node
    result = (
        db.query(models.Dam, models.Node)
        .join(models.Node, models.Dam.id == models.Node.id)
        .filter(models.Dam.id == dam_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Dam not found")

    dam, node = result

    # Get last 2 measurements for this dam
    measurements = (
        db.query(models.DamBulletinMeasurement)
        .filter(models.DamBulletinMeasurement.dam_id == dam_id)
        .order_by(models.DamBulletinMeasurement.timestamp.desc())
        .limit(2)
        .all()
    )
    # Reverse to get chronological order
    measurements.reverse()

    # Return combined dam info
    return {
        **dam.__dict__,
        "border_geometry": flip_coordinates(dam.border_geometry),
        "display_name": node.display_name,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
        "places": [
            {"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name}
            for place in dam.places
        ],
        "measurements": measurements,
    }


@app.patch("/dams/{dam_id}", response_model=schema.Dam)
def update_dam(dam_id: UUID, dam: schema.DamUpdate, db: Session = Depends(get_db)):
    try:
        # Get existing dam and node
        result = (
            db.query(models.Dam, models.Node)
            .join(models.Node, models.Dam.id == models.Node.id)
            .filter(models.Dam.id == dam_id)
            .first()
        )
        if not result:
            raise HTTPException(status_code=404, detail="Dam not found")

        db_dam, db_node = result

        # Update node fields if provided
        if dam.display_name is not None:
            db_node.display_name = dam.display_name
        if dam.latitude is not None:
            db_node.latitude = dam.latitude
        if dam.longitude is not None:
            db_node.longitude = dam.longitude

        # Update dam fields if provided
        if dam.border_geometry is not None:
            db_dam.border_geometry = dam.border_geometry
        if dam.max_volume is not None:
            db_dam.max_volume = dam.max_volume
        if dam.description is not None:
            db_dam.description = dam.description
        if dam.municipality is not None:
            db_dam.municipality = dam.municipality
        if dam.owner is not None:
            db_dam.owner = dam.owner
        if dam.owner_contact is not None:
            db_dam.owner_contact = dam.owner_contact
        if dam.operator is not None:
            db_dam.operator = dam.operator
        if dam.operator_contact is not None:
            db_dam.operator_contact = dam.operator_contact

        # Update places if provided
        if dam.place_ids is not None:
            places = db.query(models.Place).filter(models.Place.id.in_(dam.place_ids)).all()
            db_dam.places = places

        db.commit()
        db.refresh(db_dam)
        db.refresh(db_node)

        # Return combined dam info
        return {
            **db_dam.__dict__,
            "display_name": db_node.display_name,
            "latitude": db_node.latitude,
            "longitude": db_node.longitude,
            "created_at": db_node.created_at,
            "updated_at": db_node.updated_at,
            "places": [
                {"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name}
                for place in db_dam.places
            ],
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dams/{dam_id}/measurements", response_model=list[schema.DamBulletinMeasurement])
def get_dam_measurements(dam_id: UUID, db: Session = Depends(get_db)):
    return (
        db.query(models.DamBulletinMeasurement)
        .filter(models.DamBulletinMeasurement.dam_id == dam_id)
        .order_by(models.DamBulletinMeasurement.timestamp.asc())
        .all()
    )


@app.post("/dams/{dam_id}/measurements", response_model=schema.DamBulletinMeasurement)
def create_dam_measurement(
    dam_id: UUID, measurement: schema.DamBulletinMeasurementCreate, db: Session = Depends(get_db)
):
    db_measurement = models.DamBulletinMeasurement(**measurement.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


# Place endpoints
@app.post("/places", response_model=schema.Place)
def create_place(place: schema.PlaceCreate, db: Session = Depends(get_db)):
    try:
        # Create node first
        node_id = uuid.uuid4()
        db_node = models.Node(
            id=node_id,
            display_name=place.display_name,
            latitude=place.latitude,
            longitude=place.longitude,
            node_type="place",
        )
        db.add(db_node)
        db.flush()  # Ensure the node is created before the place

        # Create place with same ID
        db_place = models.Place(
            id=node_id,
            population=place.population,
            consumption_per_capita=place.consumption_per_capita,
            water_price=place.water_price,
            non_dam_incoming_flow=place.non_dam_incoming_flow,
            radius=place.radius,
            municipality=place.municipality,
        )
        db.add(db_place)

        # Commit both records in a single transaction
        db.commit()
        db.refresh(db_place)
        db.refresh(db_node)

        # Return combined place info
        return {
            **db_place.__dict__,
            "display_name": db_node.display_name,
            "latitude": db_node.latitude,
            "longitude": db_node.longitude,
            "created_at": db_node.created_at,
            "updated_at": db_node.updated_at,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/places", response_model=list[schema.Place])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    places = (
        db.query(models.Place, models.Node)
        .join(models.Node, models.Place.id == models.Node.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            **place.__dict__,
            "display_name": node.display_name,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
        }
        for place, node in places
    ]


@app.get("/places/{place_id}", response_model=schema.Place)
def read_place(place_id: UUID, db: Session = Depends(get_db)):
    result = (
        db.query(models.Place, models.Node)
        .join(models.Node, models.Place.id == models.Node.id)
        .filter(models.Place.id == place_id)
        .first()
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Place not found")
    place, node = result
    return {
        **place.__dict__,
        "display_name": node.display_name,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
    }


@app.get("/places/{place_id}/route", response_model=schema.ShortestPathResponse)
def get_route_to_closest_dam(place_id: UUID, db: Session = Depends(get_db)):
    # Get the place and its closest dam
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    if not place.closest_dam_id:
        raise HTTPException(status_code=404, detail="Place has no connected dam")

    # Get the path from place to its closest dam
    return get_shortest_path(place_id, place.closest_dam_id, db)


@app.get("/points/{latitude}/{longitude}/route", response_model=schema.PointRouteResponse)
def get_route_to_closest_dam_from_point(
    latitude: float, longitude: float, db: Session = Depends(get_db)
):
    # Find the place that we're inside of (center and radius)
    places = (
        db.query(models.Place, models.Node)
        .join(models.Node, models.Place.id == models.Node.id)
        .all()
    )

    point_location = (float(latitude), float(longitude))
    containing_place = None
    containing_place_node = None

    for place, node in places:
        place_location = (float(node.latitude), float(node.longitude))
        # Calculate distance in meters
        distance = (
            calculate_spherical_distance(
                point_location[0], point_location[1], place_location[0], place_location[1]
            )
            * 1000
        )  # Convert km to meters

        if distance <= float(place.radius):
            containing_place = place
            containing_place_node = node
            break

    if not containing_place:
        raise HTTPException(status_code=404, detail="Point is not inside any place")

    if not containing_place.closest_dam_id:
        raise HTTPException(status_code=404, detail="Place has no connected dam")

    # Get the path from place to its closest dam
    path_response = get_shortest_path(containing_place.id, containing_place.closest_dam_id, db)

    # Create a point node for the starting location
    point_node = schema.PointNode(
        id="point", node_type="point", latitude=float(latitude), longitude=float(longitude)
    )

    # Calculate distances from the point
    path_nodes = [point_node] + path_response["path"]

    # Update distances_from_start for all nodes in the path
    current_distance = 0.0
    for i in range(1, len(path_nodes)):
        prev_node = path_nodes[i - 1]
        curr_node = path_nodes[i]

        # Calculate distance between nodes
        distance = (
            calculate_spherical_distance(
                float(prev_node["latitude"] if isinstance(prev_node, dict) else prev_node.latitude),
                float(
                    prev_node["longitude"] if isinstance(prev_node, dict) else prev_node.longitude
                ),
                float(curr_node["latitude"]),
                float(curr_node["longitude"]),
            )
            * 1000
        )  # Convert km to meters

        current_distance += float(distance)
        curr_node["distance_from_start"] = current_distance

    # Create place info
    place_info = {
        "id": containing_place.id,
        "display_name": containing_place_node.display_name,
        "latitude": float(containing_place_node.latitude),
        "longitude": float(containing_place_node.longitude),
        "created_at": containing_place_node.created_at,
        "updated_at": containing_place_node.updated_at,
        "population": containing_place.population,
        "consumption_per_capita": float(containing_place.consumption_per_capita),
        "water_price": float(containing_place.water_price),
        "non_dam_incoming_flow": float(containing_place.non_dam_incoming_flow),
        "radius": float(containing_place.radius),
        "municipality": containing_place.municipality,
        "closest_dam_id": containing_place.closest_dam_id,
    }

    total_consumption = 0  # m³/month
    total_dam_outflow = 0  # m³/month
    total_natural_inflow = 0  # m³/month

    for node in path_nodes:
        if isinstance(node, dict):
            if node["node_type"] == "place":
                # Calculate monthly consumption: (m³/person/day) * persons * 30 days
                daily_consumption = float(node["place_data"]["consumption_per_capita"]) * float(
                    node["place_data"]["population"]
                )
                total_consumption += daily_consumption * 30

                # Add natural inflow: (m³/day) * 30 days
                daily_natural = float(node["place_data"]["non_dam_incoming_flow"])
                total_natural_inflow += daily_natural * 30

            elif node["node_type"] == "dam":
                # Get latest measurement for this dam
                latest_measurement = (
                    db.query(models.DamBulletinMeasurement)
                    .filter(models.DamBulletinMeasurement.dam_id == node["id"])
                    .order_by(models.DamBulletinMeasurement.timestamp.desc())
                    .first()
                )

                if latest_measurement:
                    # Add the measurement to the node for display
                    node["latest_measurement"] = {
                        "id": latest_measurement.id,
                        "timestamp": latest_measurement.timestamp,
                        "volume": float(latest_measurement.volume),
                        "fill_volume": float(latest_measurement.fill_volume),
                        "avg_incoming_flow": float(latest_measurement.avg_incoming_flow),
                        "avg_outgoing_flow": float(latest_measurement.avg_outgoing_flow),
                    }
                    # Calculate monthly outflow: (m³/day) * 30 days
                    total_dam_outflow += float(latest_measurement.avg_outgoing_flow) * 30
                else:
                    node["latest_measurement"] = None

    return {
        "path": path_nodes,
        "total_distance": current_distance,
        "place": place_info,
        "water_metrics": {
            "total_consumption": total_consumption,  # m³/month
            "total_dam_outflow": total_dam_outflow,  # m³/month
            "total_natural_inflow": total_natural_inflow,  # m³/month
            "net_water_balance": total_dam_outflow
            + total_natural_inflow
            - total_consumption,  # m³/month
        },
    }


@app.patch("/places/{place_id}/closest-dam/{dam_id}", response_model=schema.Place)
def update_place_closest_dam(place_id: UUID, dam_id: UUID, db: Session = Depends(get_db)):
    # Verify both place and dam exist
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    dam = db.query(models.Dam).filter(models.Dam.id == dam_id).first()
    if not dam:
        raise HTTPException(status_code=404, detail="Dam not found")

    # Update the closest dam
    place.closest_dam_id = dam_id
    db.commit()

    # Return updated place with node info
    result = (
        db.query(models.Place, models.Node)
        .join(models.Node, models.Place.id == models.Node.id)
        .filter(models.Place.id == place_id)
        .first()
    )
    place, node = result
    return {
        **place.__dict__,
        "display_name": node.display_name,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
    }


# Junction endpoints
@app.post("/junctions", response_model=schema.Junction)
def create_junction(junction: schema.JunctionCreate, db: Session = Depends(get_db)):
    try:
        # Create node first
        node_id = uuid.uuid4()
        db_node = models.Node(
            id=node_id,
            display_name=junction.display_name,
            latitude=junction.latitude,
            longitude=junction.longitude,
            node_type="junction",
        )
        db.add(db_node)
        db.flush()  # Ensure the node is created before the junction

        # Create junction with same ID
        db_junction = models.Junction(
            id=node_id,
            source_node_id=junction.source_node_id,
            target_node_id=junction.target_node_id,
            max_flow_rate=junction.max_flow_rate,
            current_flow_rate=junction.current_flow_rate,
            length=junction.length,
        )
        db.add(db_junction)

        # Commit both records in a single transaction
        db.commit()
        db.refresh(db_junction)
        db.refresh(db_node)

        # Return combined junction info
        return {
            **db_junction.__dict__,
            "display_name": db_node.display_name,
            "latitude": db_node.latitude,
            "longitude": db_node.longitude,
            "created_at": db_node.created_at,
            "updated_at": db_node.updated_at,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/junctions", response_model=list[schema.Junction])
def read_junctions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    junctions = (
        db.query(models.Junction, models.Node)
        .join(models.Node, models.Junction.id == models.Node.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            **junction.__dict__,
            "display_name": node.display_name,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
        }
        for junction, node in junctions
    ]


@app.get("/junctions/{junction_id}", response_model=schema.Junction)
def read_junction(junction_id: UUID, db: Session = Depends(get_db)):
    result = (
        db.query(models.Junction, models.Node)
        .join(models.Node, models.Junction.id == models.Node.id)
        .filter(models.Junction.id == junction_id)
        .first()
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Junction not found")
    junction, node = result
    return {
        **junction.__dict__,
        "display_name": node.display_name,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
    }


# Edge endpoints
@app.post("/edges", response_model=schema.Edge)
def create_edge(edge: schema.EdgeCreate, db: Session = Depends(get_db)):
    try:
        # Get source and target nodes to calculate distance
        source_node = db.query(models.Node).filter(models.Node.id == edge.source_node_id).first()
        target_node = db.query(models.Node).filter(models.Node.id == edge.target_node_id).first()

        if not source_node or not target_node:
            raise HTTPException(status_code=404, detail="Source or target node not found")

        # Calculate distance in meters
        distance_km = calculate_spherical_distance(
            float(source_node.latitude),
            float(source_node.longitude),
            float(target_node.latitude),
            float(target_node.longitude),
        )
        distance_meters = distance_km * 1000  # Convert to meters

        # Create edge
        db_edge = models.Edge(
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            distance=distance_meters,
            description=edge.description,
        )
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        return db_edge
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/edges", response_model=list[schema.Edge])
def read_edges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Edge).offset(skip).limit(limit).all()


@app.get("/edges/{edge_id}", response_model=schema.Edge)
def read_edge(edge_id: UUID, db: Session = Depends(get_db)):
    db_edge = db.query(models.Edge).filter(models.Edge.id == edge_id).first()
    if db_edge is None:
        raise HTTPException(status_code=404, detail="Edge not found")
    return db_edge


# Dam Bulletin Measurement endpoints
@app.get("/measurements", response_model=list[schema.DamBulletinMeasurement])
def read_measurements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(models.DamBulletinMeasurement)
        .order_by(models.DamBulletinMeasurement.timestamp.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get("/measurements/{measurement_id}", response_model=schema.DamBulletinMeasurement)
def read_measurement(measurement_id: UUID, db: Session = Depends(get_db)):
    db_measurement = (
        db.query(models.DamBulletinMeasurement)
        .filter(models.DamBulletinMeasurement.id == measurement_id)
        .first()
    )
    if db_measurement is None:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return db_measurement


# Dam Prediction endpoints
@app.post("/dams/{dam_id}/predictions", response_model=schema.DamPrediction)
def create_dam_prediction(
    dam_id: UUID, prediction: schema.DamPredictionCreate, db: Session = Depends(get_db)
):
    # Get the dam's max volume first
    dam = db.query(models.Dam).filter(models.Dam.id == prediction.dam_id).first()
    if not dam:
        raise HTTPException(status_code=404, detail="Dam not found")

    db_prediction = models.DamPrediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    # Calculate fill percentage
    db_prediction.fill_percentage = (db_prediction.fill_volume / dam.max_volume) * 100

    return db_prediction


@app.get("/dams/{dam_id}/predictions", response_model=list[schema.DamPrediction])
def get_dam_predictions(dam_id: UUID, db: Session = Depends(get_db)):
    # Get the dam's max volume first
    dam = db.query(models.Dam).filter(models.Dam.id == dam_id).first()
    if not dam:
        raise HTTPException(status_code=404, detail="Dam not found")

    # Get predictions and calculate percentages
    predictions = (
        db.query(models.DamPrediction)
        .filter(models.DamPrediction.dam_id == dam_id)
        .order_by(models.DamPrediction.timestamp.asc())
        .all()
    )

    for prediction in predictions:
        prediction.fill_percentage = (prediction.fill_volume / dam.max_volume) * 100

    return predictions


@app.get("/predictions", response_model=list[schema.DamPrediction])
def read_predictions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Get predictions with their corresponding dams
    predictions = (
        db.query(models.DamPrediction, models.Dam)
        .join(models.Dam, models.DamPrediction.dam_id == models.Dam.id)
        .order_by(models.DamPrediction.timestamp.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Calculate fill percentages
    result = []
    for prediction, dam in predictions:
        prediction.fill_percentage = (prediction.fill_volume / dam.max_volume) * 100
        result.append(prediction)

    return result


@app.get("/predictions/{prediction_id}", response_model=schema.DamPrediction)
def read_prediction(prediction_id: UUID, db: Session = Depends(get_db)):
    # Get prediction with its dam
    result = (
        db.query(models.DamPrediction, models.Dam)
        .join(models.Dam, models.DamPrediction.dam_id == models.Dam.id)
        .filter(models.DamPrediction.id == prediction_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Prediction not found")

    prediction, dam = result
    prediction.fill_percentage = (prediction.fill_volume / dam.max_volume) * 100

    return prediction


# Satellite Image endpoints
@app.post("/satellite-images", response_model=schema.SatelliteImage)
def create_satellite_image(image: schema.SatelliteImageCreate, db: Session = Depends(get_db)):
    db_image = models.SatelliteImage(**image.model_dump())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


@app.get("/satellite-images", response_model=list[schema.SatelliteImage])
def read_satellite_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.SatelliteImage).offset(skip).limit(limit).all()


# User Bill Form endpoints
@app.post("/bill-forms", response_model=schema.UserBillForm)
def create_bill_form(form: schema.UserBillFormCreate, db: Session = Depends(get_db)):
    db_form = models.UserBillForm(**form.model_dump())
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return db_form


@app.get("/bill-forms", response_model=list[schema.UserBillForm])
def read_bill_forms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.UserBillForm).offset(skip).limit(limit).all()


# Newsletter Subscription endpoints
@app.post("/newsletter", response_model=schema.NewsletterSubscription)
def create_subscription(
    subscription: schema.NewsletterSubscriptionCreate, db: Session = Depends(get_db)
):
    db_subscription = models.NewsletterSubscription(**subscription.model_dump())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@app.get("/newsletter", response_model=list[schema.NewsletterSubscription])
def read_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.NewsletterSubscription).offset(skip).limit(limit).all()


# Dam Alert endpoints
@app.post("/alerts", response_model=schema.DamAlert)
def create_alert(alert: schema.DamAlertCreate, db: Session = Depends(get_db)):
    db_alert = models.DamAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@app.get("/alerts", response_model=list[schema.DamAlert])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.DamAlert).offset(skip).limit(limit).all()


@app.get("/alerts/{alert_id}", response_model=schema.DamAlert)
def read_alert(alert_id: UUID, db: Session = Depends(get_db)):
    db_alert = db.query(models.DamAlert).filter(models.DamAlert.id == alert_id).first()
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert
