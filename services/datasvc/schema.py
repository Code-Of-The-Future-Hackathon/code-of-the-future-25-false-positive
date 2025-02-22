from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional, Dict, Any

from pydantic import UUID4, BaseModel, EmailStr, Field


class NodeFieldsMixin(BaseModel):
    display_name: str
    latitude: Decimal
    longitude: Decimal


class NodeBase(NodeFieldsMixin):
    node_type: Literal["dam", "place", "junction"]


class NodeCreate(NodeBase):
    pass


class NodeResponseMixin(NodeFieldsMixin):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Node(NodeBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EdgeBase(BaseModel):
    source_node_id: UUID4
    target_node_id: UUID4
    description: Optional[str] = None


class EdgeCreate(EdgeBase):
    pass


class Edge(EdgeBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    distance: Decimal

    class Config:
        from_attributes = True


class PlaceRef(BaseModel):
    id: UUID4
    display_name: str

    class Config:
        from_attributes = True


class DamBase(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    border_geometry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GeoJSON MultiPolygon object"
    )
    max_volume: Decimal
    description: str = ""
    municipality: str = ""
    owner: Optional[str] = None
    owner_contact: Optional[str] = None
    operator: Optional[str] = None
    operator_contact: Optional[str] = None


class DamCreate(DamBase, NodeFieldsMixin):
    place_ids: list[UUID4] = Field(default_factory=list)


class Dam(DamBase, NodeResponseMixin):
    places: list[PlaceRef] = Field(default_factory=list)


class PlaceBase(BaseModel):
    population: int
    consumption_per_capita: Decimal
    water_price: Decimal
    non_dam_incoming_flow: Decimal
    radius: Decimal
    municipality: str = ""


class PlaceCreate(PlaceBase, NodeFieldsMixin):
    pass


class Place(PlaceBase, NodeResponseMixin):
    pass


class JunctionBase(BaseModel):
    max_flow_rate: Decimal
    current_flow_rate: Optional[Decimal] = None
    length: Decimal
    source_node_id: UUID4
    target_node_id: UUID4


class JunctionCreate(JunctionBase, NodeFieldsMixin):
    pass


class Junction(JunctionBase, NodeResponseMixin):
    pass


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
    model_config = {"arbitrary_types_allowed": True}
    
    dam_id: UUID4
    timestamp: datetime
    image_url: str
    bounding_box: str = Field(
        description="GeoJSON Polygon string"
    )


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
