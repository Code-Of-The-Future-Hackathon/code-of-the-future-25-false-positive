from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schema
from database import engine, get_db

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="False Positive")


# Node endpoints
@app.post("/nodes", response_model=schema.Node)
def create_node(node: schema.NodeCreate, db: Session = Depends(get_db)):
    db_node = models.Node(**node.model_dump())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


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
def create_dam(dam: schema.DamCreate, node_id: UUID, db: Session = Depends(get_db)):
    db_dam = models.Dam(id=node_id, **dam.model_dump())
    db.add(db_dam)
    db.commit()
    db.refresh(db_dam)
    return db_dam


@app.get("/dams", response_model=list[schema.Dam])
def read_dams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Dam).offset(skip).limit(limit).all()


@app.get("/dams/{dam_id}", response_model=schema.Dam)
def read_dam(dam_id: UUID, db: Session = Depends(get_db)):
    db_dam = db.query(models.Dam).filter(models.Dam.id == dam_id).first()
    if db_dam is None:
        raise HTTPException(status_code=404, detail="Dam not found")
    return db_dam


# Place endpoints
@app.post("/places", response_model=schema.Place)
def create_place(place: schema.PlaceCreate, node_id: UUID, db: Session = Depends(get_db)):
    db_place = models.Place(id=node_id, **place.model_dump())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


@app.get("/places", response_model=list[schema.Place])
def read_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Place).offset(skip).limit(limit).all()


@app.get("/places/{place_id}", response_model=schema.Place)
def read_place(place_id: UUID, db: Session = Depends(get_db)):
    db_place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if db_place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place


# Water Connection endpoints
@app.post("/connections", response_model=schema.WaterConnection)
def create_connection(connection: schema.WaterConnectionCreate, db: Session = Depends(get_db)):
    db_connection = models.WaterConnection(**connection.model_dump())
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection


@app.get("/connections", response_model=list[schema.WaterConnection])
def read_connections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.WaterConnection).offset(skip).limit(limit).all()


@app.get("/connections/{connection_id}", response_model=schema.WaterConnection)
def read_connection(connection_id: UUID, db: Session = Depends(get_db)):
    db_connection = (
        db.query(models.WaterConnection).filter(models.WaterConnection.id == connection_id).first()
    )
    if db_connection is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    return db_connection


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
