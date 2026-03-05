import os
import time
from pathlib import Path
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def __init__(self, api_base: str, incoming_dir: Path):
        self.api_base = api_base.rstrip("/")
        self.incoming_dir = incoming_dir

    def on_created(self, event):
        if event.is_directory:
            return

        p = Path(event.src_path)

        # Solo miramos json/pdf/img por ahora (ajustamos después)
        if p.suffix.lower() not in [".json", ".pdf", ".png", ".jpg", ".jpeg"]:
            return

        # Esperar que Windows termine de copiar/escribir
        for _ in range(40):
            try:
                s1 = p.stat().st_size
                time.sleep(0.25)
                s2 = p.stat().st_size
                if s1 == s2 and s2 > 0:
                    break
            except FileNotFoundError:
                return

        rel = str(p.relative_to(self.incoming_dir)).replace("/", "\\")
        payload = {
            "kind": "raw_ocr" if p.suffix.lower() == ".json" else "file",
            "source_path": f"incoming\\{rel}",
            "payload": {}
        }

        url = f"{self.api_base}/ingest"
        try:
            r = requests.post(url, json=payload, timeout=20)
            print("[INGEST]", r.status_code, rel, r.text[:200])
        except Exception as e:
            print("[ERR] ingest", rel, e)

def main():
    api_base = os.environ.get("ABM_API", "http://127.0.0.1:8000")
    incoming = os.environ.get("ABM_INCOMING", r"C:\ABM_STACK\incoming")
    incoming_dir = Path(incoming)

    print("Watcher ON")
    print(" ABM_API     =", api_base)
    print(" ABM_INCOMING=", incoming)

    h = Handler(api_base, incoming_dir)
    obs = Observer()
    obs.schedule(h, str(incoming_dir), recursive=True)
    obs.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()

    obs.join()

if __name__ == "__main__":
    main()