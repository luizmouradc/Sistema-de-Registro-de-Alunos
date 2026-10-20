from __future__ import annotations

import csv
import io
import uuid
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from config import PHOTOS_DIR


EXPORT_FIELDS = [
    "id", "matricula", "nome", "email", "telefone", "sexo",
    "data_nascimento", "endereco", "curso", "periodo", "status",
]

IMPORT_REQUIRED = {"matricula", "nome", "email", "curso"}


def save_photo(data: bytes, original_name: str) -> str:
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(original_name).suffix.lower()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        suffix = ".jpg"
    filename = f"{uuid.uuid4().hex}{suffix}"
    path = PHOTOS_DIR / filename
    path.write_bytes(data)
    return str(path)


def to_csv_bytes(students: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in students:
        writer.writerow({key: row.get(key, "") for key in EXPORT_FIELDS})
    return stream.getvalue().encode("utf-8-sig")


def to_xlsx_bytes(students: list[dict[str, Any]]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Alunos"
    ws.append(EXPORT_FIELDS)
    for row in students:
        ws.append([row.get(key, "") for key in EXPORT_FIELDS])

    widths = {
        "A": 8, "B": 18, "C": 34, "D": 32, "E": 18, "F": 20,
        "G": 18, "H": 36, "I": 32, "J": 10, "K": 14,
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def parse_csv_bytes(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("O CSV não possui cabeçalho.")

    names = {name.strip() for name in reader.fieldnames if name}
    missing = IMPORT_REQUIRED - names
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))

    rows: list[dict[str, str]] = []
    for raw in reader:
        row = {str(k).strip(): (v or "").strip() for k, v in raw.items() if k is not None}
        if any(row.values()):
            rows.append(row)
    return rows
