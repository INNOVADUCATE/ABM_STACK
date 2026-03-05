import json
import hashlib
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import SessionLocal, engine, Base, get_db
from .models import Socio, Artifact
from .schemas import SocioCreate, SocioOut, IngestRequest, IngestResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"service": "abm-api", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest, db: Session = Depends(get_db)):
    raw = json.dumps(req.payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()

    art = Artifact(
        kind=req.kind,
        source_path=req.source_path,
        sha256=sha,
        payload=req.payload,
        status="queued",
        processed_at=None,
        error=None,
    )

    db.add(art)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="artifact_duplicado")

    db.refresh(art)
    return IngestResponse(id=art.id, kind=art.kind, source_path=art.source_path, sha256=art.sha256)

@app.post("/socios", response_model=SocioOut)
def create_socio(payload: SocioCreate):
    db = SessionLocal()
    try:
        socio = Socio(
            nombre=payload.nombre.strip(),
            matricula=payload.matricula.strip(),
            estado="activo",
        )
        db.add(socio)
        db.commit()
        db.refresh(socio)
        return socio

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="matricula_duplicada")

    finally:
        db.close()