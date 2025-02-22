import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import DECIMAL, UUID
from sqlalchemy.sql import func

from database import Base


class Node(Base):
    __tablename__ = "nodes"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String, nullable=False)
    latitude = Column(DECIMAL, nullable=False)
    longitude = Column(DECIMAL, nullable=False)
    node_type = Column(
        Enum("dam", "place", "junction", name="node_type", schema="false_positive"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Dam(Base):
    __tablename__ = "dams"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), primary_key=True)
    border_geometry = Column(Geometry("MULTIPOLYGON", srid=4326))
    max_volume = Column(DECIMAL)  # m³
    description = Column(Text, server_default="")


class Place(Base):
    __tablename__ = "places"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), primary_key=True)
    population = Column(Integer)
    consumption_per_capita = Column(DECIMAL)  # m³/person/day
    water_price = Column(DECIMAL)  # BGN/m³
    non_dam_incoming_flow = Column(DECIMAL)  # m³/s
    radius = Column(DECIMAL)  # meters


class WaterConnection(Base):
    __tablename__ = "water_connections"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_node_id = Column(
        UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), nullable=False
    )
    target_node_id = Column(
        UUID(as_uuid=True), ForeignKey("false_positive.nodes.id"), nullable=False
    )
    max_flow_rate = Column(DECIMAL)  # m³/s
    current_flow_rate = Column(DECIMAL, nullable=True)  # m³/s
    length = Column(DECIMAL)  # meters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DamBulletinMeasurement(Base):
    __tablename__ = "dam_bulletin_measurements"
    __table_args__ = {"schema": "false_positive"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dam_id = Column(UUID(as_uuid=True), ForeignKey("false_positive.dams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    volume = Column(DECIMAL)  # m³
    fill_volume = Column(DECIMAL)  # m³
    avg_incoming_flow = Column(DECIMAL)  # m³/s
    avg_outgoing_flow = Column(DECIMAL)  # m³/s


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
