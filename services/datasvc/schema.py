from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import UUID4, BaseModel, EmailStr, Field
from shapely.geometry import MultiPolygon, Polygon


class NodeBase(BaseModel):
    display_name: str
    latitude: Decimal
    longitude: Decimal
    node_type: Literal["dam", "place", "junction"]


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DamBase(BaseModel):
    border_geometry: Optional[MultiPolygon] = None
    max_volume: Decimal
    description: str = ""


class DamCreate(DamBase):
    pass


class Dam(DamBase):
    id: UUID4

    class Config:
        from_attributes = True


class PlaceBase(BaseModel):
    population: int
    consumption_per_capita: Decimal
    water_price: Decimal
    non_dam_incoming_flow: Decimal
    radius: Decimal


class PlaceCreate(PlaceBase):
    pass


class Place(PlaceBase):
    id: UUID4

    class Config:
        from_attributes = True


class WaterConnectionBase(BaseModel):
    source_node_id: UUID4
    target_node_id: UUID4
    max_flow_rate: Decimal
    current_flow_rate: Optional[Decimal] = None
    length: Decimal


class WaterConnectionCreate(WaterConnectionBase):
    pass


class WaterConnection(WaterConnectionBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DamBulletinMeasurementBase(BaseModel):
    dam_id: UUID4
    timestamp: datetime
    volume: Decimal
    fill_volume: Decimal
    avg_incoming_flow: Decimal
    avg_outgoing_flow: Decimal


class DamBulletinMeasurementCreate(DamBulletinMeasurementBase):
    pass


class DamBulletinMeasurement(DamBulletinMeasurementBase):
    id: UUID4

    class Config:
        from_attributes = True


class SatelliteImageBase(BaseModel):
    dam_id: UUID4
    timestamp: datetime
    image_url: str
    bounding_box: Polygon


class SatelliteImageCreate(SatelliteImageBase):
    pass


class SatelliteImage(SatelliteImageBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class UserBillFormBase(BaseModel):
    place_id: UUID4
    start_date: date
    end_date: date


class UserBillFormCreate(UserBillFormBase):
    pass


class UserBillForm(UserBillFormBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class NewsletterSubscriptionBase(BaseModel):
    email: EmailStr


class NewsletterSubscriptionCreate(NewsletterSubscriptionBase):
    pass


class NewsletterSubscription(NewsletterSubscriptionBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DamAlertBase(BaseModel):
    dam_id: UUID4
    severity: Literal["info", "warning", "critical"]
    timestamp: datetime
    message: str


class DamAlertCreate(DamAlertBase):
    pass


class DamAlert(DamAlertBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
