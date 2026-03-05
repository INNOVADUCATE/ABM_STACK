from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .db import Base


class Socio(Base):
    __tablename__ = "socios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    matricula = Column(String, nullable=False, unique=True, index=True)
    estado = Column(String, nullable=False, default="activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(50), nullable=False, index=True)
    source_path = Column(String(500), nullable=False)
    sha256 = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    status = Column(String(20), nullable=False, default="queued", index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error = Column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint("sha256", name="uq_artifacts_sha256"),
    )