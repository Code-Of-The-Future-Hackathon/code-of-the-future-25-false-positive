from datetime import date, datetime
from typing import Literal, Optional, Dict, Any, Union

from pydantic import UUID4, BaseModel, EmailStr, Field


class NodeFieldsMixin(BaseModel):
    display_name: str
    latitude: float
    longitude: float


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
    volume: float
    fill_volume: float
    avg_incoming_flow: float
    avg_outgoing_flow: float


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
    max_volume: float
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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    border_geometry: Optional[Dict[str, Any]] = None
    max_volume: Optional[float] = None
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
    max_volume: float
    description: str
    municipality: str
    owner: Optional[str] = None
    operator: Optional[str] = None

    class Config:
        from_attributes = True


class ShortestPathPlaceData(BaseModel):
    population: int
    consumption_per_capita: float
    water_price: float
    non_dam_incoming_flow: float
    radius: float
    municipality: str

    class Config:
        from_attributes = True


class ShortestPathJunctionData(BaseModel):
    max_flow_rate: float
    current_flow_rate: Optional[float] = None
    length: float
    source_node_id: UUID4
    target_node_id: UUID4

    class Config:
        from_attributes = True


class ShortestPathNode(BaseModel):
    id: UUID4
    node_type: str
    display_name: str
    latitude: float
    longitude: float
    distance_from_start: float
    dam_data: Optional[ShortestPathDamData] = None
    place_data: Optional[ShortestPathPlaceData] = None
    junction_data: Optional[ShortestPathJunctionData] = None

    class Config:
        from_attributes = True


class ShortestPathResponse(BaseModel):
    path: list[ShortestPathNode]
    total_distance: float

    class Config:
        from_attributes = True


class PointNode(BaseModel):
    id: Literal["point"]  # Special ID to identify this as a point node
    node_type: Literal["point"]
    display_name: str = "Вашия адрес"
    latitude: float
    longitude: float
    distance_from_start: float = 0.0

    class Config:
        from_attributes = True


class WaterMetrics(BaseModel):
    total_consumption: float = Field(description="Total water consumption in cubic meters per month")
    total_dam_outflow: float = Field(description="Total water provided by dams in cubic meters per month")
    total_natural_inflow: float = Field(description="Total water from natural sources in cubic meters per month")
    net_water_balance: float = Field(description="Net water balance (supply - demand) in cubic meters per month")


class PointRouteResponse(BaseModel):
    path: list[Union[PointNode, ShortestPathNode]]
    total_distance: float
    place: 'Place'
    water_metrics: WaterMetrics

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
    distance: float

    class Config:
        from_attributes = True


class PlaceBase(BaseModel):
    population: int
    consumption_per_capita: float
    water_price: float
    non_dam_incoming_flow: float
    radius: float
    municipality: str = ""
    closest_dam_id: Optional[UUID4] = None


class PlaceCreate(PlaceBase, NodeFieldsMixin):
    pass


class Place(PlaceBase, NodeResponseMixin):
    pass


class JunctionBase(BaseModel):
    max_flow_rate: float
    current_flow_rate: Optional[float] = None
    length: float
    source_node_id: UUID4
    target_node_id: UUID4


class JunctionCreate(JunctionBase, NodeFieldsMixin):
    pass


class Junction(JunctionBase, NodeResponseMixin):
    pass


class DamPredictionBase(BaseModel):
    dam_id: UUID4
    timestamp: datetime
    fill_volume: float


class DamPredictionCreate(DamPredictionBase):
    pass


class DamPrediction(DamPredictionBase):
    id: UUID4
    created_at: datetime
    fill_percentage: float = Field(description="Percentage of the dam's maximum volume that is filled")

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
