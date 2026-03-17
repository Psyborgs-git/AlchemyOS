"""SQLAlchemy ORM models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, Enum, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MoleculeModel(Base):
    """SQLAlchemy model for molecules table."""

    __tablename__ = "molecules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    smiles = Column(String(500), nullable=False, index=True)
    inchi = Column(Text, nullable=False)
    inchi_key = Column(String(27), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=True)
    formula = Column(String(100), nullable=False)
    mol_weight = Column(Float, nullable=False)
    properties = Column(JSON, nullable=False, default=dict)
    source = Column(String(50), nullable=False, default="user")
    safety_status = Column(String(50), nullable=False, default="clear")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    experiment_id = Column(UUID(as_uuid=True), nullable=True)


class MolecularPropertyModel(Base):
    """SQLAlchemy model for molecular_properties table."""

    __tablename__ = "molecular_properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    molecule_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    property_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    method = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
