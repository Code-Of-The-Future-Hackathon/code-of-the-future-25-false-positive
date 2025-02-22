import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, Numeric, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, nullable=False)
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    node_type = Column(
        Enum("dam", "place", "junction", name="node_type", schema="false_positive"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Association table for dam-place relationship
dam_places = Table(
    "dam_places",
    Base.metadata,
    Column("dam_id", UUID(as_uuid=True), ForeignKey("false_positive.dams.id"), primary_key=True),
    Column("place_id", UUID(as_uuid=True), ForeignKey("false_positive.places.id"), primary_key=True),
    schema="false_positive"
)

class Dam(Base):
    __tablename__ = "dams"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), primary_key=True)
    border_geometry = Column(JSONB)  # GeoJSON MultiPolygon
    max_volume = Column(Numeric)  # m³
    description = Column(Text, server_default="")
    municipality = Column(String, nullable=False)  # Municipality name
    owner = Column(String, nullable=True)
    owner_contact = Column(String, nullable=True)
    operator = Column(String, nullable=True)
    operator_contact = Column(String, nullable=True)
    
    # Relationship with places
    places = relationship("Place", secondary=dam_places, backref="dams")


class Place(Base):
    __tablename__ = "places"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), primary_key=True)
    population = Column(Integer)
    consumption_per_capita = Column(Numeric)  # m³/person/day
    water_price = Column(Numeric)  # BGN/m³
    non_dam_incoming_flow = Column(Numeric)  # m³/s
    radius = Column(Numeric)  # meters
    municipality = Column(String, nullable=False)  # Municipality name


class Junction(Base):
    __tablename__ = "junctions"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), primary_key=True)
    source_node_id = Column(
        UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), nullable=False
    )
    target_node_id = Column(
        UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), nullable=False
    )
    max_flow_rate = Column(Numeric)  # m³/s
    current_flow_rate = Column(Numeric, nullable=True)  # m³/s
    length = Column(Numeric)  # meters


class DamBulletinMeasurement(Base):
    __tablename__ = "dam_bulletin_measurements"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dam_id = Column(UUID(as_uuid=True), ForeignKey("false_positive.dams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    volume = Column(Numeric)  # m³
    fill_volume = Column(Numeric)  # m³
    avg_incoming_flow = Column(Numeric)  # m³/s
    avg_outgoing_flow = Column(Numeric)  # m³/s


class SatelliteImage(Base):
    __tablename__ = "satellite_images"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dam_id = Column(UUID(as_uuid=True), ForeignKey("false_positive.dams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    image_url = Column(String, nullable=False)
    bounding_box = Column(Geometry("POLYGON", srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserBillForm(Base):
    __tablename__ = "user_bill_forms"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id = Column(UUID(as_uuid=True), ForeignKey("false_positive.places.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DamAlert(Base):
    __tablename__ = "dam_alerts"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dam_id = Column(UUID(as_uuid=True), ForeignKey("false_positive.dams.id"), nullable=False)
    severity = Column(
        Enum("info", "warning", "critical", name="alert_severity", schema="false_positive"),
        nullable=False,
    )
    timestamp = Column(DateTime(timezone=True), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
