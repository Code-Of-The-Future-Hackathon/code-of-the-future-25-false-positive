from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional, Dict, Any, Union

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


class PlaceRef(BaseModel):
    id: UUID4
    display_name: str

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


class DamUpdate(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    
    display_name: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    border_geometry: Optional[Dict[str, Any]] = None
    max_volume: Optional[Decimal] = None
    description: Optional[str] = None
    municipality: Optional[str] = None
    owner: Optional[str] = None
    owner_contact: Optional[str] = None
    operator: Optional[str] = None
    operator_contact: Optional[str] = None
    place_ids: Optional[list[UUID4]] = None


class Dam(DamBase, NodeResponseMixin):
    places: list[PlaceRef] = Field(default_factory=list)
    measurements: list[DamBulletinMeasurement] = Field(default_factory=list, description="Last 2 measurements in chronological order")


class ShortestPathDamData(BaseModel):
    max_volume: Decimal
    description: str
    municipality: str
    owner: Optional[str] = None
    operator: Optional[str] = None

    class Config:
        from_attributes = True


class ShortestPathPlaceData(BaseModel):
    population: int
    consumption_per_capita: Decimal
    water_price: Decimal
    non_dam_incoming_flow: Decimal
    radius: Decimal
    municipality: str

    class Config:
        from_attributes = True


class ShortestPathJunctionData(BaseModel):
    max_flow_rate: Decimal
    current_flow_rate: Optional[Decimal] = None
    length: Decimal
    source_node_id: UUID4
    target_node_id: UUID4

    class Config:
        from_attributes = True


class ShortestPathNode(BaseModel):
    id: UUID4
    node_type: str
    display_name: str
    latitude: Decimal
    longitude: Decimal
    distance_from_start: Decimal
    dam_data: Optional[ShortestPathDamData] = None
    place_data: Optional[ShortestPathPlaceData] = None
    junction_data: Optional[ShortestPathJunctionData] = None

    class Config:
        from_attributes = True


class ShortestPathResponse(BaseModel):
    path: list[ShortestPathNode]
    total_distance: Decimal

    class Config:
        from_attributes = True


class PointNode(BaseModel):
    id: Literal["point"]  # Special ID to identify this as a point node
    node_type: Literal["point"]
    display_name: str = "Current Location"
    latitude: Decimal
    longitude: Decimal
    distance_from_start: Decimal = Decimal('0')

    class Config:
        from_attributes = True


class PointRouteResponse(BaseModel):
    path: list[Union[PointNode, ShortestPathNode]]
    total_distance: Decimal
    place: Place  # Include the place we're inside of

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


class PlaceBase(BaseModel):
    population: int
    consumption_per_capita: Decimal
    water_price: Decimal
    non_dam_incoming_flow: Decimal
    radius: Decimal
    municipality: str = ""
    closest_dam_id: Optional[UUID4] = None


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


class DamPredictionBase(BaseModel):
    dam_id: UUID4
    timestamp: datetime
    fill_volume: Decimal


class DamPredictionCreate(DamPredictionBase):
    pass


class DamPrediction(DamPredictionBase):
    id: UUID4
    created_at: datetime
    fill_percentage: Decimal = Field(description="Percentage of the dam's maximum volume that is filled")

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


class ComplaintBase(BaseModel):
    user_email: EmailStr
    subject: str
    description: str
    status: Literal["pending", "in_progress", "resolved"] = "pending"
    place_id: Optional[UUID4] = None
    dam_id: Optional[UUID4] = None


class ComplaintCreate(ComplaintBase):
    pass


class Complaint(ComplaintBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
