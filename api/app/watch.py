import os
import json
import time
import requests
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API = os.getenv("ABM_API", "http://127.0.0.1:8000")
INCOMING = os.getenv("ABM_INCOMING", r"C:\ABM_STACK\incoming")

def guess_kind(filename: str) -> str:
    f = filename.lower()
    if "raw" in f and "ocr" in f:
        return "raw_ocr"
    if "analisis" in f and "clasificado" not in f and "aportes" not in f:
        return "analisis_abm"
    if "clasificado" in f:
        return "clasificado"
    if "aportes" in f:
        return "aportes"
    if "estado" in f:
        return "estado"
    return "unknown"

def post_ingest(path: str):
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    body = {
        "kind": guess_kind(os.path.basename(path)),
        "source_path": path,
        "payload": payload
    }

    r = requests.post(f"{API}/ingest", json=body, timeout=30)
    if r.status_code in (200, 201):
        print("OK ingest:", os.path.basename(path), "->", r.json().get("id"))
    elif r.status_code == 409:
        print("SKIP duplicado:", os.path.basename(path))
    else:
        print("ERROR ingest:", r.status_code, r.text)

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.lower().endswith(".json"):
            return

        # mini-wait por si el archivo todavía se está escribiendo
        time.sleep(0.3)
        try:
            post_ingest(event.src_path)
        except Exception as e:
            print("ERROR:", event.src_path, e)

if __name__ == "__main__":
    os.makedirs(INCOMING, exist_ok=True)
    obs = Observer()
    obs.schedule(Handler(), INCOMING, recursive=False)
    obs.start()
    print("Watcher ON:", INCOMING, "->", API)
    try:
        while True:
            time.sleep(1)
    finally:
        obs.stop()
        obs.join()