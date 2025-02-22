from uuid import UUID
import uuid

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import text
from decimal import Decimal

from . import models
from . import schema
from .database import engine, get_db
from .utils import calculate_spherical_distance

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="False Positive")


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
def get_shortest_path(
    start_node_id: UUID,
    end_node_id: UUID,
    db: Session = Depends(get_db)
):
    # First verify both nodes exist
    start_node = db.query(models.Node).filter(models.Node.id == start_node_id).first()
    end_node = db.query(models.Node).filter(models.Node.id == end_node_id).first()
    
    if not start_node or not end_node:
        raise HTTPException(status_code=404, detail="Start or end node not found")
    
    # Get the shortest path using pgr_dijkstra
    setup_query = text("""
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
    """)
    
    path_query = text("""
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
    """)
    
    cleanup_query = text("""
        DROP TABLE IF EXISTS temp_node_mapping;
        DROP TABLE IF EXISTS temp_edge_mapping;
    """)
    
    try:
        # Setup temporary tables
        db.execute(setup_query)
        
        # Get the path
        result = db.execute(
            path_query,
            {"start": str(start_node_id), "end": str(end_node_id)}
        ).fetchall()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No path found between the specified nodes"
            )
        
        # Convert the results to our response format
        path_nodes = []
        for row in result:
            node_data = {
                "id": row.id,
                "node_type": row.node_type,
                "display_name": row.display_name,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "distance_from_start": Decimal(str(row.distance_from_start))
            }
            
            # Add type-specific data
            if row.node_type == "dam" and row.dam_max_volume is not None:
                node_data["dam_data"] = {
                    "max_volume": row.dam_max_volume,
                    "description": row.dam_description,
                    "municipality": row.dam_municipality,
                    "owner": row.dam_owner,
                    "operator": row.dam_operator
                }
            elif row.node_type == "place" and row.place_population is not None:
                node_data["place_data"] = {
                    "population": row.place_population,
                    "consumption_per_capita": row.place_consumption_per_capita,
                    "water_price": row.place_water_price,
                    "non_dam_incoming_flow": row.place_non_dam_incoming_flow,
                    "radius": row.place_radius,
                    "municipality": row.place_municipality
                }
            elif row.node_type == "junction" and row.junction_max_flow_rate is not None:
                node_data["junction_data"] = {
                    "max_flow_rate": row.junction_max_flow_rate,
                    "current_flow_rate": row.junction_current_flow_rate,
                    "length": row.junction_length,
                    "source_node_id": row.junction_source_node_id,
                    "target_node_id": row.junction_target_node_id
                }
            
            path_nodes.append(node_data)
        
        # Total distance is the distance_from_start of the last node
        total_distance = path_nodes[-1]["distance_from_start"] if path_nodes else Decimal('0')
        
        return {
            "path": path_nodes,
            "total_distance": total_distance
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating shortest path: {str(e)}"
        )
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
            node_type="dam"
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
            operator_contact=dam.operator_contact
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
            "display_name": db_node.display_name,
            "latitude": db_node.latitude,
            "longitude": db_node.longitude,
            "created_at": db_node.created_at,
            "updated_at": db_node.updated_at,
            "places": [{"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name} 
                      for place in db_dam.places]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dams", response_model=list[schema.Dam])
def read_dams(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None, 
    db: Session = Depends(get_db)
):
    # Base query joining Dam with its Node
    PlaceNode = aliased(models.Node)
    query = (
        db.query(models.Dam, models.Node, models.Place, PlaceNode.display_name.label('place_display_name'))
        .join(models.Node, models.Dam.id == models.Node.id)
        .outerjoin(models.dam_places, models.Dam.id == models.dam_places.c.dam_id)
        .outerjoin(models.Place, models.dam_places.c.place_id == models.Place.id)
        .outerjoin(PlaceNode, models.Place.id == PlaceNode.id)
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            PlaceNode.display_name.ilike(search_term) |
            models.Dam.municipality.ilike(search_term) |
            PlaceNode.display_name.ilike(search_term)
        )
    
    # First get the dam IDs we want to return
    dam_ids = [
        dam_id for dam_id, in 
        query.with_entities(models.Dam.id)
        .distinct()
        .offset(skip)
        .limit(limit)
        .all()
    ]
    
    # Then fetch complete data for these dams
    final_query = (
        db.query(
            models.Dam,
            models.Node,
            models.Place,
            PlaceNode.display_name.label('place_display_name')
        )
        .join(models.Node, models.Dam.id == models.Node.id)
        .outerjoin(models.dam_places, models.Dam.id == models.dam_places.c.dam_id)
        .outerjoin(models.Place, models.dam_places.c.place_id == models.Place.id)
        .outerjoin(PlaceNode, models.Place.id == PlaceNode.id)
        .filter(models.Dam.id.in_(dam_ids))
    )
    
    # Process results
    results = final_query.all()
    
    # Group results by dam
    dams_dict = {}
    for dam, node, place, place_display_name in results:
        if dam.id not in dams_dict:
            dams_dict[dam.id] = {
                **dam.__dict__,
                "display_name": node.display_name,
                "latitude": node.latitude,
                "longitude": node.longitude,
                "created_at": node.created_at,
                "updated_at": node.updated_at,
                "places": []
            }
        if place and place.id:  # Only add place if it exists
            place_info = {"id": place.id, "display_name": place_display_name}
            if place_info not in dams_dict[dam.id]["places"]:
                dams_dict[dam.id]["places"].append(place_info)
    
    # Return results in the same order as the IDs
    return [dams_dict[dam_id] for dam_id in dam_ids]


@app.get("/dams/{dam_id}", response_model=schema.Dam)
def read_dam(dam_id: UUID, db: Session = Depends(get_db)):
    result = (
        db.query(models.Dam, models.Node)
        .join(models.Node, models.Dam.id == models.Node.id)
        .filter(models.Dam.id == dam_id)
        .first()
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Dam not found")
    dam, node = result
    return {
        **dam.__dict__,
        "display_name": node.display_name,
        "latitude": node.latitude,
        "longitude": node.longitude,
        "created_at": node.created_at,
        "updated_at": node.updated_at,
        "places": [{"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name} 
                  for place in dam.places]
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
            "places": [{"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name} 
                      for place in db_dam.places]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


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
            node_type="place"
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
            municipality=place.municipality
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
            "updated_at": db_node.updated_at
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
def get_route_to_closest_dam(
    place_id: UUID,
    db: Session = Depends(get_db)
):
    # Get the place and its closest dam
    place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    if not place.closest_dam_id:
        raise HTTPException(status_code=404, detail="Place has no connected dam")
    
    # Get the path from place to its closest dam
    return get_shortest_path(place_id, place.closest_dam_id, db)


@app.patch("/places/{place_id}/closest-dam/{dam_id}", response_model=schema.Place)
def update_place_closest_dam(
    place_id: UUID,
    dam_id: UUID,
    db: Session = Depends(get_db)
):
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
            node_type="junction"
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
            length=junction.length
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
            "updated_at": db_node.updated_at
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
            float(target_node.longitude)
        )
        distance_meters = distance_km * 1000  # Convert to meters
        
        # Create edge
        db_edge = models.Edge(
            source_node_id=edge.source_node_id,
            target_node_id=edge.target_node_id,
            distance=distance_meters,
            description=edge.description
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
@app.post("/measurements", response_model=schema.DamBulletinMeasurement)
def create_measurement(
    measurement: schema.DamBulletinMeasurementCreate, db: Session = Depends(get_db)
):
    db_measurement = models.DamBulletinMeasurement(**measurement.model_dump())
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement


@app.get("/measurements", response_model=list[schema.DamBulletinMeasurement])
def read_measurements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.DamBulletinMeasurement).offset(skip).limit(limit).all()


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
