from pydantic import BaseModel, Field
from typing import Any, Dict


class SocioCreate(BaseModel):
    nombre: str
    matricula: str


class SocioOut(BaseModel):
    id: int
    nombre: str
    matricula: str
    estado: str

    class Config:
        from_attributes = True


class IngestRequest(BaseModel):
    kind: str = Field(..., examples=["raw_ocr", "analisis_abm", "clasificado", "aportes", "estado"])
    source_path: str
    payload: Dict[str, Any]


class IngestResponse(BaseModel):
    id: int
    kind: str
    source_path: str
    sha256: str