import os
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Artifact

POLL_SECONDS = float(os.getenv("POLL_SECONDS", "2.0"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "20"))

def process_artifact(a: Artifact) -> None:
    """
    Acá va tu lógica real.
    Por ahora, simulamos "OK" si payload existe, si no -> error.
    """
    if a.payload is None:
        raise ValueError("payload vacío")
    # Simulación de procesamiento:
    # - en el futuro: parsear payload, validar, extraer campos, etc.
    return

def main():
    print("[job_runner] starting…")
    print(f"[job_runner] poll={POLL_SECONDS}s batch={BATCH_SIZE}")

    while True:
        try:
            with SessionLocal() as db:  # type: Session
                q = (
                    select(Artifact)
                    .where(Artifact.status == "queued")
                    .order_by(Artifact.id.asc())
                    .limit(BATCH_SIZE)
                )
                items = db.execute(q).scalars().all()

                if not items:
                    time.sleep(POLL_SECONDS)
                    continue

                for a in items:
                    # lock "lógico" simple: marcamos processing primero
                    a.status = "processing"
                    a.error = None
                    db.commit()

                    try:
                        process_artifact(a)
                        a.status = "processed"
                        a.processed_at = datetime.now(timezone.utc)
                        a.error = None
                        db.commit()
                        print(f"[job_runner] OK id={a.id} kind={a.kind} src={a.source_path}")
                    except Exception as e:
                        a.status = "failed"
                        a.error = str(e)[:500]
                        db.commit()
                        print(f"[job_runner] FAIL id={a.id} err={a.error}")

        except Exception as outer:
            print(f"[job_runner] loop error: {outer}")
            time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()