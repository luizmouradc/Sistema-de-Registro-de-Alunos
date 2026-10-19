from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from config import DB_PATH, DATA_DIR, LEGACY_DB_PATH


class StudentRepository:
    def __init__(self, db_path: Path = DB_PATH):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path)
        self._copy_legacy_database_if_needed()
        self._initialize()

    def _copy_legacy_database_if_needed(self) -> None:
        """Copia um estudantes.db da V1 para data/ na primeira execução."""
        if not self.db_path.exists() and LEGACY_DB_PATH.exists() and LEGACY_DB_PATH != self.db_path:
            shutil.copy2(LEGACY_DB_PATH, self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alunos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matricula TEXT NOT NULL UNIQUE,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefone TEXT NOT NULL DEFAULT '',
                    sexo TEXT NOT NULL DEFAULT '',
                    data_nascimento TEXT NOT NULL DEFAULT '',
                    endereco TEXT NOT NULL DEFAULT '',
                    curso TEXT NOT NULL,
                    periodo INTEGER,
                    status TEXT NOT NULL DEFAULT 'Ativo',
                    foto TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alunos_nome ON alunos(nome)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alunos_curso ON alunos(curso)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alunos_status ON alunos(status)")
            self._migrate_v1_if_present(conn)
            conn.commit()

    def _migrate_v1_if_present(self, conn: sqlite3.Connection) -> None:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='estudantes'"
        ).fetchone()
        if not exists:
            return

        # Evita duplicar migração em execuções futuras.
        already = conn.execute("SELECT COUNT(*) AS n FROM alunos").fetchone()["n"]
        if already:
            return

        columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(estudantes)").fetchall()
        }
        required = {
            "id", "nome", "email", "telefone", "sexo", "data_nascimento",
            "endereco", "curso", "picture"
        }
        if not required.issubset(columns):
            return

        now = datetime.now().isoformat(timespec="seconds")
        students = conn.execute(
            "SELECT id, nome, email, telefone, sexo, data_nascimento, endereco, curso, picture "
            "FROM estudantes ORDER BY id"
        ).fetchall()

        for row in students:
            conn.execute(
                """
                INSERT OR IGNORE INTO alunos
                (matricula, nome, email, telefone, sexo, data_nascimento, endereco,
                 curso, periodo, status, foto, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"MIGRADO-{row['id']:05d}",
                    row["nome"], row["email"], row["telefone"],
                    {"M": "Masculino", "F": "Feminino"}.get(row["sexo"], row["sexo"]),
                    row["data_nascimento"], row["endereco"], row["curso"],
                    None, "Ativo", row["picture"] or "", now, now,
                ),
            )

    def list_students(
        self,
        search: str = "",
        course: str = "Todos",
        status: str = "Todos",
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if search.strip():
            term = f"%{search.strip()}%"
            clauses.append(
                "(nome LIKE ? OR matricula LIKE ? OR email LIKE ? OR CAST(id AS TEXT) LIKE ?)"
            )
            params.extend([term, term, term, term])
        if course and course != "Todos":
            clauses.append("curso = ?")
            params.append(course)
        if status and status != "Todos":
            clauses.append("status = ?")
            params.append(status)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM alunos {where} ORDER BY nome COLLATE NOCASE"
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def get_student(self, student_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM alunos WHERE id = ?", (student_id,)).fetchone()
            return dict(row) if row else None

    def create_student(self, data: dict[str, Any]) -> int:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO alunos
                (matricula, nome, email, telefone, sexo, data_nascimento, endereco,
                 curso, periodo, status, foto, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["matricula"], data["nome"], data["email"], data.get("telefone", ""),
                    data.get("sexo", ""), data.get("data_nascimento", ""), data.get("endereco", ""),
                    data["curso"], data.get("periodo"), data.get("status", "Ativo"),
                    data.get("foto", ""), now, now,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_student(self, student_id: int, data: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE alunos SET
                    matricula=?, nome=?, email=?, telefone=?, sexo=?, data_nascimento=?,
                    endereco=?, curso=?, periodo=?, status=?, foto=?, updated_at=?
                WHERE id=?
                """,
                (
                    data["matricula"], data["nome"], data["email"], data.get("telefone", ""),
                    data.get("sexo", ""), data.get("data_nascimento", ""), data.get("endereco", ""),
                    data["curso"], data.get("periodo"), data.get("status", "Ativo"),
                    data.get("foto", ""), now, student_id,
                ),
            )
            conn.commit()

    def delete_student(self, student_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM alunos WHERE id=?", (student_id,))
            conn.commit()

    def matricula_exists(self, matricula: str, ignore_id: int | None = None) -> bool:
        query = "SELECT id FROM alunos WHERE matricula = ?"
        params: list[Any] = [matricula]
        if ignore_id is not None:
            query += " AND id <> ?"
            params.append(ignore_id)
        with self._connect() as conn:
            return conn.execute(query, params).fetchone() is not None

    def stats(self) -> dict[str, int]:
        month_prefix = datetime.now().strftime("%Y-%m")
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) n FROM alunos").fetchone()["n"]
            active = conn.execute("SELECT COUNT(*) n FROM alunos WHERE status='Ativo'").fetchone()["n"]
            courses = conn.execute("SELECT COUNT(DISTINCT curso) n FROM alunos").fetchone()["n"]
            new_month = conn.execute(
                "SELECT COUNT(*) n FROM alunos WHERE created_at LIKE ?",
                (f"{month_prefix}%",),
            ).fetchone()["n"]
        return {"total": total, "active": active, "courses": courses, "new_month": new_month}

    def recent_students(self, limit: int = 5) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM alunos ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(row) for row in rows]

    def course_summary(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT curso,
                       COUNT(*) AS total,
                       SUM(CASE WHEN status='Ativo' THEN 1 ELSE 0 END) AS ativos,
                       SUM(CASE WHEN status='Formado' THEN 1 ELSE 0 END) AS formados
                FROM alunos
                GROUP BY curso
                ORDER BY total DESC, curso COLLATE NOCASE
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def all_courses(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT curso FROM alunos WHERE TRIM(curso) <> '' ORDER BY curso COLLATE NOCASE"
            ).fetchall()
            return [row["curso"] for row in rows]

    def database_bytes(self) -> bytes:
        # Garante que conexões anteriores tenham sido fechadas (todos os métodos usam context manager).
        return self.db_path.read_bytes()
