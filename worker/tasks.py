# worker/tasks.py

import os
from celery import Celery
from PIL import Image
import pytesseract

# Broker-URL zieht Celery aus der Umgebung (docker-compose)
broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery("worker", broker=broker)

@app.task
def ocr_file(filename: str):
    """
    Liest /worker/storage/filename, führt OCR aus
    und schreibt das Ergebnis in filename + '.txt'.
    """
    storage_dir = "/worker/storage"
    img_path = os.path.join(storage_dir, filename)
    txt_path = img_path + ".txt"

    # OCR durchführen
    text = pytesseract.image_to_string(Image.open(img_path))

    # Ergebnis speichern
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return {"file": filename, "chars": len(text)}
