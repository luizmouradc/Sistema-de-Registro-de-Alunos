from __future__ import annotations

import re
from datetime import datetime
from typing import Any


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def validate_student(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not str(data.get("nome", "")).strip():
        errors.append("Informe o nome do aluno.")
    if not str(data.get("matricula", "")).strip():
        errors.append("Informe a matrícula.")
    if not str(data.get("curso", "")).strip():
        errors.append("Selecione o curso.")

    email = str(data.get("email", "")).strip()
    if not email:
        errors.append("Informe o e-mail.")
    elif not EMAIL_RE.fullmatch(email):
        errors.append("Informe um e-mail válido.")

    phone = normalize_phone(str(data.get("telefone", "")))
    if phone and not 8 <= len(phone) <= 15:
        errors.append("O telefone deve ter entre 8 e 15 dígitos.")

    birth = str(data.get("data_nascimento", "")).strip()
    if birth:
        try:
            datetime.strptime(birth, "%d/%m/%Y")
        except ValueError:
            errors.append("A data de nascimento deve estar no formato dd/mm/aaaa.")

    period = data.get("periodo")
    if period not in (None, ""):
        try:
            value = int(period)
            if value < 1 or value > 20:
                raise ValueError
        except (TypeError, ValueError):
            errors.append("O período deve ser um número entre 1 e 20.")

    return errors
