from uuid import UUID
import uuid

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schema
from database import engine, get_db

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
            municipality=dam.municipality
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
def read_dams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dams = (
        db.query(models.Dam, models.Node)
        .join(models.Node, models.Dam.id == models.Node.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            **dam.__dict__,
            "display_name": node.display_name,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
            "places": [{"id": place.id, "display_name": db.query(models.Node).get(place.id).display_name} 
                      for place in dam.places]
        }
        for dam, node in dams
    ]


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
