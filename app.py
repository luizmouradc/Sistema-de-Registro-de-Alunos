from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import flet as ft

from components.ui import empty_state, section_title, stat_card, status_badge
from config import (
    APP_NAME, BACKGROUND, BORDER, CURSOS_PADRAO, DANGER, INDIGO, INDIGO_DARK,
    INDIGO_SOFT, NAVY, NAVY_2, SEXOS, STATUS_ALUNO, SUCCESS, SURFACE, TEXT,
    TEXT_MUTED,
)
from database.repository import StudentRepository
from services.files import parse_csv_bytes, save_photo, to_csv_bytes, to_xlsx_bytes
from services.validators import normalize_phone, validate_student


class AcademicApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.repo = StudentRepository()
        self.current_view = "dashboard"
        self.search_value = ""
        self.course_filter = "Todos"
        self.status_filter = "Todos"
        self.selected_photo_path = ""
        self.selected_photo_bytes: bytes | None = None

        self.page.title = APP_NAME
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = BACKGROUND
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=INDIGO)
        self.page.window.min_width = 1050
        self.page.window.min_height = 680

        self.render()

    # ---------- Helpers ----------
    def notify(self, message: str, error: bool = False) -> None:
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, color="#FFFFFF"),
                bgcolor=DANGER if error else SUCCESS,
            )
        )

    def show_errors(self, errors: list[str]) -> None:
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Revise os dados"),
            content=ft.Column(
                tight=True,
                controls=[ft.Text(f"• {item}") for item in errors],
            ),
            actions=[ft.TextButton("Fechar", on_click=lambda e: self.page.pop_dialog())],
        )
        self.page.show_dialog(dialog)

    def courses(self) -> list[str]:
        saved = self.repo.all_courses()
        return sorted(set(CURSOS_PADRAO + saved), key=str.casefold)

    def nav(self, view: str) -> None:
        self.current_view = view
        self.render()

    # ---------- Shell ----------
    def nav_button(self, label: str, icon: str, view: str) -> ft.Button:
        active = self.current_view == view
        return ft.Button(
            content=label,
            icon=icon,
            width=205,
            height=46,
            bgcolor=INDIGO if active else NAVY,
            color="#FFFFFF" if active else "#D1D5DB",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                alignment=ft.Alignment.CENTER_LEFT,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                elevation=0,
            ),
            on_click=lambda e: self.nav(view),
        )

    def build_sidebar(self) -> ft.Container:
        return ft.Container(
            width=250,
            bgcolor=NAVY,
            padding=20,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                bgcolor=INDIGO,
                                border_radius=12,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.SCHOOL_ROUNDED, color="#FFFFFF", size=24),
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text("Gestão", size=17, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    ft.Text("Acadêmica", size=12, color="#9CA3AF"),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(height=28),
                    self.nav_button("Dashboard", ft.Icons.DASHBOARD_ROUNDED, "dashboard"),
                    self.nav_button("Alunos", ft.Icons.GROUP_ROUNDED, "students"),
                    self.nav_button("Cursos", ft.Icons.SCHOOL_OUTLINED, "courses"),
                    self.nav_button("Dados e backup", ft.Icons.CLOUD_DOWNLOAD_OUTLINED, "data"),
                    ft.Container(expand=True),
                    ft.Container(height=1, bgcolor=NAVY_2),
                    ft.Container(height=10),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.CircleAvatar(
                                radius=18,
                                bgcolor=INDIGO_SOFT,
                                content=ft.Icon(ft.Icons.PERSON_OUTLINE, size=18, color=INDIGO),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=0,
                                controls=[
                                    ft.Text("Administrador", size=13, color="#F9FAFB", weight=ft.FontWeight.W_600),
                                    ft.Text("Sistema local", size=11, color="#9CA3AF"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    def build_topbar(self) -> ft.Container:
        titles = {
            "dashboard": "Visão geral",
            "students": "Alunos",
            "courses": "Cursos",
            "data": "Dados e backup",
        }
        return ft.Container(
            height=72,
            bgcolor=SURFACE,
            border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
            padding=ft.Padding.symmetric(horizontal=28, vertical=14),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(titles[self.current_view], size=18, weight=ft.FontWeight.W_600, color=TEXT),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=12, vertical=7),
                                border=ft.Border.all(1, BORDER),
                                border_radius=12,
                                content=ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.STORAGE_ROUNDED, size=17, color=TEXT_MUTED),
                                        ft.Text("SQLite local", size=12, color=TEXT_MUTED),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def render(self) -> None:
        content = {
            "dashboard": self.dashboard_view,
            "students": self.students_view,
            "courses": self.courses_view,
            "data": self.data_view,
        }[self.current_view]()

        self.page.controls.clear()
        self.page.add(
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    self.build_sidebar(),
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            self.build_topbar(),
                            ft.Container(
                                expand=True,
                                bgcolor=BACKGROUND,
                                padding=28,
                                content=content,
                            ),
                        ],
                    ),
                ],
            )
        )
        self.page.update()

    # ---------- Dashboard ----------
    def dashboard_view(self) -> ft.Control:
        stats = self.repo.stats()
        recent = self.repo.recent_students(5)
        summary = self.repo.course_summary()
        max_total = max((item["total"] for item in summary), default=1)

        recent_controls: list[ft.Control] = []
        for student in recent:
            recent_controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                    border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                radius=18,
                                bgcolor=INDIGO_SOFT,
                                content=ft.Text(student["nome"][:1].upper(), color=INDIGO, weight=ft.FontWeight.BOLD),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=1,
                                controls=[
                                    ft.Text(student["nome"], size=13, weight=ft.FontWeight.W_600, color=TEXT),
                                    ft.Text(f"{student['matricula']} • {student['curso']}", size=11, color=TEXT_MUTED),
                                ],
                            ),
                            status_badge(student["status"]),
                        ],
                    ),
                )
            )

        if not recent_controls:
            recent_controls.append(empty_state(ft.Icons.GROUP_OUTLINED, "Nenhum aluno cadastrado", "Cadastre o primeiro aluno para começar."))

        course_controls: list[ft.Control] = []
        for item in summary[:6]:
            course_controls.append(
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(item["curso"], size=12, color=TEXT, weight=ft.FontWeight.W_500),
                                ft.Text(str(item["total"]), size=12, color=TEXT_MUTED),
                            ],
                        ),
                        ft.ProgressBar(value=item["total"] / max_total, color=INDIGO, bgcolor="#E5E7EB", height=7),
                    ],
                )
            )
        if not course_controls:
            course_controls.append(ft.Text("Os cursos aparecerão aqui conforme os cadastros.", color=TEXT_MUTED, size=13))

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        section_title("Dashboard", "Acompanhe rapidamente os principais dados acadêmicos."),
                        ft.Button(
                            content="Novo aluno",
                            icon=ft.Icons.ADD_ROUNDED,
                            bgcolor=INDIGO,
                            color="#FFFFFF",
                            on_click=lambda e: self.open_student_form(),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=14,
                    controls=[
                        stat_card("Alunos cadastrados", str(stats["total"]), ft.Icons.GROUP_ROUNDED),
                        stat_card("Alunos ativos", str(stats["active"]), ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, SUCCESS, "#DCFCE7"),
                        stat_card("Cursos", str(stats["courses"]), ft.Icons.SCHOOL_OUTLINED, "#2563EB", "#DBEAFE"),
                        stat_card("Novos no mês", str(stats["new_month"]), ft.Icons.PERSON_ADD_ALT_1_ROUNDED, "#D97706", "#FEF3C7"),
                    ],
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=16,
                    controls=[
                        ft.Container(
                            expand=2,
                            bgcolor=SURFACE,
                            border=ft.Border.all(1, BORDER),
                            border_radius=16,
                            content=ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Container(
                                        padding=18,
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text("Cadastros recentes", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                                                ft.TextButton("Ver todos", on_click=lambda e: self.nav("students")),
                                            ],
                                        ),
                                    ),
                                    *recent_controls,
                                ],
                            ),
                        ),
                        ft.Container(
                            expand=1,
                            padding=18,
                            bgcolor=SURFACE,
                            border=ft.Border.all(1, BORDER),
                            border_radius=16,
                            content=ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Text("Alunos por curso", size=16, weight=ft.FontWeight.W_600, color=TEXT),
                                    *course_controls,
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        )

    # ---------- Students ----------
    def _student_table(self, students: list[dict]) -> ft.Control:
        rows: list[ft.DataRow] = []
        for student in students:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.CircleAvatar(
                                        radius=16,
                                        bgcolor=INDIGO_SOFT,
                                        content=ft.Text(student["nome"][:1].upper(), color=INDIGO, size=12, weight=ft.FontWeight.BOLD),
                                    ),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(student["nome"], size=12, weight=ft.FontWeight.W_600, color=TEXT),
                                            ft.Text(student["email"], size=10, color=TEXT_MUTED),
                                        ],
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(ft.Text(student["matricula"], size=12)),
                        ft.DataCell(ft.Text(student["curso"], size=12)),
                        ft.DataCell(ft.Text(str(student["periodo"] or "-"), size=12)),
                        ft.DataCell(status_badge(student["status"])),
                        ft.DataCell(
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        tooltip="Editar",
                                        icon_color=INDIGO,
                                        on_click=lambda e, sid=student["id"]: self.open_student_form(sid),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                        tooltip="Excluir",
                                        icon_color=DANGER,
                                        on_click=lambda e, sid=student["id"]: self.confirm_delete(sid),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )

        if not rows:
            return empty_state(
                ft.Icons.SEARCH_OFF_ROUNDED,
                "Nenhum aluno encontrado",
                "Tente remover algum filtro ou cadastre um novo aluno.",
            )

        return ft.Row(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.DataTable(
                    border_radius=12,
                    heading_row_color="#F9FAFB",
                    heading_text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600, color=TEXT_MUTED),
                    data_text_style=ft.TextStyle(size=12, color=TEXT),
                    data_row_min_height=58,
                    data_row_max_height=58,
                    column_spacing=34,
                    columns=[
                        ft.DataColumn(label=ft.Text("Aluno")),
                        ft.DataColumn(label=ft.Text("Matrícula")),
                        ft.DataColumn(label=ft.Text("Curso")),
                        ft.DataColumn(label=ft.Text("Período")),
                        ft.DataColumn(label=ft.Text("Status")),
                        ft.DataColumn(label=ft.Text("Ações")),
                    ],
                    rows=rows,
                )
            ],
        )

    def students_view(self) -> ft.Control:
        initial_students = self.repo.list_students(self.search_value, self.course_filter, self.status_filter)
        results_text = ft.Text(f"{len(initial_students)} registro(s) encontrado(s).", size=14, color=TEXT_MUTED)
        table_host = ft.Container(
            expand=True,
            padding=10,
            bgcolor=SURFACE,
            border=ft.Border.all(1, BORDER),
            border_radius=16,
            content=self._student_table(initial_students),
        )

        def refresh_results() -> None:
            students = self.repo.list_students(self.search_value, self.course_filter, self.status_filter)
            results_text.value = f"{len(students)} registro(s) encontrado(s)."
            table_host.content = self._student_table(students)
            results_text.update()
            table_host.update()

        def search_changed(e) -> None:
            self.search_value = e.control.value or ""
            refresh_results()

        def course_changed(e) -> None:
            self.course_filter = e.control.value or "Todos"
            refresh_results()

        def status_changed(e) -> None:
            self.status_filter = e.control.value or "Todos"
            refresh_results()

        search = ft.TextField(
            value=self.search_value,
            hint_text="Nome, matrícula, e-mail ou ID...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            width=360,
            height=46,
            on_change=search_changed,
        )
        course = ft.Dropdown(
            label="Curso",
            value=self.course_filter,
            width=250,
            options=[ft.DropdownOption(key="Todos", text="Todos os cursos")] + [
                ft.DropdownOption(key=item, text=item) for item in self.courses()
            ],
            on_select=course_changed,
        )
        status = ft.Dropdown(
            label="Status",
            value=self.status_filter,
            width=180,
            options=[ft.DropdownOption(key="Todos", text="Todos")] + [
                ft.DropdownOption(key=item, text=item) for item in STATUS_ALUNO
            ],
            on_select=status_changed,
        )

        return ft.Column(
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text("Alunos", size=28, weight=ft.FontWeight.BOLD, color=TEXT),
                                results_text,
                            ],
                        ),
                        ft.Button(
                            content="Novo aluno",
                            icon=ft.Icons.ADD_ROUNDED,
                            bgcolor=INDIGO,
                            color="#FFFFFF",
                            on_click=lambda e: self.open_student_form(),
                        ),
                    ],
                ),
                ft.Container(
                    padding=16,
                    bgcolor=SURFACE,
                    border=ft.Border.all(1, BORDER),
                    border_radius=16,
                    content=ft.Row(
                        wrap=True,
                        spacing=12,
                        controls=[search, course, status],
                    ),
                ),
                table_host,
            ],
        )

    # ---------- Form ----------
    def open_student_form(self, student_id: int | None = None) -> None:
        student = self.repo.get_student(student_id) if student_id else None
        self.selected_photo_path = student.get("foto", "") if student else ""
        self.selected_photo_bytes = None

        matricula = ft.TextField(label="Matrícula *", value=student.get("matricula", "") if student else "")
        nome = ft.TextField(label="Nome completo *", value=student.get("nome", "") if student else "")
        email = ft.TextField(label="E-mail *", value=student.get("email", "") if student else "")
        telefone = ft.TextField(label="Telefone", value=student.get("telefone", "") if student else "")
        nascimento = ft.TextField(
            label="Data de nascimento",
            hint_text="dd/mm/aaaa",
            value=student.get("data_nascimento", "") if student else "",
        )
        endereco = ft.TextField(label="Endereço", value=student.get("endereco", "") if student else "")
        sexo = ft.Dropdown(
            label="Sexo",
            value=student.get("sexo", "") if student else None,
            options=[ft.DropdownOption(key=item, text=item) for item in SEXOS],
        )
        curso = ft.Dropdown(
            label="Curso *",
            value=student.get("curso", "") if student else None,
            editable=True,
            enable_filter=True,
            options=[ft.DropdownOption(key=item, text=item) for item in self.courses()],
        )
        periodo = ft.TextField(
            label="Período",
            value=str(student.get("periodo") or "") if student else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        status = ft.Dropdown(
            label="Status",
            value=student.get("status", "Ativo") if student else "Ativo",
            options=[ft.DropdownOption(key=item, text=item) for item in STATUS_ALUNO],
        )

        def photo_control() -> ft.Control:
            if self.selected_photo_bytes:
                return ft.Image(src=self.selected_photo_bytes, width=90, height=90, fit=ft.BoxFit.COVER, border_radius=45)
            if self.selected_photo_path and Path(self.selected_photo_path).exists():
                try:
                    return ft.Image(src=Path(self.selected_photo_path).read_bytes(), width=90, height=90, fit=ft.BoxFit.COVER, border_radius=45)
                except OSError:
                    pass
            return ft.CircleAvatar(
                radius=45,
                bgcolor=INDIGO_SOFT,
                content=ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=INDIGO, size=38),
            )

        photo_preview = ft.Container(content=photo_control())

        async def choose_photo(e) -> None:
            files = await ft.FilePicker().pick_files(
                allow_multiple=False,
                with_data=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["png", "jpg", "jpeg", "webp", "bmp"],
            )
            if files:
                selected = files[0]
                if selected.bytes:
                    self.selected_photo_bytes = selected.bytes
                    self.selected_photo_path = save_photo(selected.bytes, selected.name)
                    photo_preview.content = photo_control()
                    photo_preview.update()

        async def save(e) -> None:
            selected_course = curso.value or curso.text or ""
            data = {
                "matricula": (matricula.value or "").strip(),
                "nome": (nome.value or "").strip(),
                "email": (email.value or "").strip(),
                "telefone": normalize_phone(telefone.value or ""),
                "sexo": sexo.value or "",
                "data_nascimento": (nascimento.value or "").strip(),
                "endereco": (endereco.value or "").strip(),
                "curso": selected_course.strip(),
                "periodo": (periodo.value or "").strip() or None,
                "status": status.value or "Ativo",
                "foto": self.selected_photo_path,
            }
            errors = validate_student(data)
            if data["matricula"] and self.repo.matricula_exists(data["matricula"], student_id):
                errors.append("Já existe um aluno com essa matrícula.")
            if errors:
                self.show_errors(errors)
                return

            if data["periodo"] is not None:
                data["periodo"] = int(data["periodo"])
            try:
                if student_id:
                    self.repo.update_student(student_id, data)
                else:
                    self.repo.create_student(data)
            except sqlite3.IntegrityError as ex:
                self.show_errors(["Não foi possível salvar. Verifique se a matrícula já está em uso."])
                return

            self.page.pop_dialog()
            self.notify("Aluno atualizado com sucesso." if student_id else "Aluno cadastrado com sucesso.")
            self.render()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar aluno" if student_id else "Novo aluno", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=720,
                height=520,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=14,
                    controls=[
                        ft.Row(
                            controls=[
                                photo_preview,
                                ft.Column(
                                    spacing=4,
                                    controls=[
                                        ft.Text("Foto do aluno", weight=ft.FontWeight.W_600),
                                        ft.Text("PNG, JPG ou WEBP. A imagem é copiada para o sistema.", size=11, color=TEXT_MUTED),
                                        ft.TextButton("Selecionar foto", icon=ft.Icons.UPLOAD_OUTLINED, on_click=choose_photo),
                                    ],
                                ),
                            ]
                        ),
                        ft.Row(controls=[ft.Container(expand=1, content=matricula), ft.Container(expand=2, content=nome)]),
                        ft.Row(controls=[ft.Container(expand=2, content=email), ft.Container(expand=1, content=telefone)]),
                        ft.Row(controls=[ft.Container(expand=1, content=nascimento), ft.Container(expand=1, content=sexo)]),
                        endereco,
                        ft.Row(controls=[ft.Container(expand=2, content=curso), ft.Container(expand=1, content=periodo), ft.Container(expand=1, content=status)]),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
                ft.Button(
                    content="Salvar alterações" if student_id else "Cadastrar aluno",
                    icon=ft.Icons.SAVE_OUTLINED,
                    bgcolor=INDIGO,
                    color="#FFFFFF",
                    on_click=save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)

    def confirm_delete(self, student_id: int) -> None:
        student = self.repo.get_student(student_id)
        if not student:
            return

        def delete(e) -> None:
            self.repo.delete_student(student_id)
            self.page.pop_dialog()
            self.notify("Aluno excluído com sucesso.")
            self.render()

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Excluir aluno?"),
                content=ft.Text(f"O cadastro de {student['nome']} será removido permanentemente."),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
                    ft.Button(content="Excluir", bgcolor=DANGER, color="#FFFFFF", on_click=delete),
                ],
            )
        )

    # ---------- Courses ----------
    def courses_view(self) -> ft.Control:
        summary = self.repo.course_summary()
        total = sum(item["total"] for item in summary) or 1
        cards: list[ft.Control] = []
        for item in summary:
            percent = item["total"] / total
            cards.append(
                ft.Container(
                    padding=18,
                    bgcolor=SURFACE,
                    border=ft.Border.all(1, BORDER),
                    border_radius=16,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(item["curso"], size=15, weight=ft.FontWeight.W_600, color=TEXT),
                                            ft.Text(f"{item['ativos']} ativo(s) • {item['formados']} formado(s)", size=11, color=TEXT_MUTED),
                                        ],
                                    ),
                                    ft.Text(str(item["total"]), size=26, weight=ft.FontWeight.BOLD, color=INDIGO),
                                ],
                            ),
                            ft.ProgressBar(value=percent, color=INDIGO, bgcolor="#E5E7EB", height=7),
                        ],
                    ),
                )
            )

        if not cards:
            cards = [empty_state(ft.Icons.SCHOOL_OUTLINED, "Ainda não há cursos com alunos", "Os dados desta tela são gerados automaticamente pelos cadastros.")]

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[
                section_title("Cursos", "Resumo automático dos alunos por curso."),
                *cards,
            ],
        )

    # ---------- Data / import / export / backup ----------
    def data_view(self) -> ft.Control:
        async def export_csv(e) -> None:
            data = to_csv_bytes(self.repo.list_students())
            path = await ft.FilePicker().save_file(
                dialog_title="Exportar alunos em CSV",
                file_name=f"alunos_{datetime.now():%Y%m%d}.csv",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"],
                src_bytes=data,
            )
            if path or self.page.web:
                self.notify("CSV exportado com sucesso.")

        async def export_xlsx(e) -> None:
            data = to_xlsx_bytes(self.repo.list_students())
            path = await ft.FilePicker().save_file(
                dialog_title="Exportar alunos em Excel",
                file_name=f"alunos_{datetime.now():%Y%m%d}.xlsx",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx"],
                src_bytes=data,
            )
            if path or self.page.web:
                self.notify("Planilha exportada com sucesso.")

        async def backup(e) -> None:
            path = await ft.FilePicker().save_file(
                dialog_title="Salvar backup do banco",
                file_name=f"backup_estudantes_{datetime.now():%Y%m%d_%H%M}.db",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["db"],
                src_bytes=self.repo.database_bytes(),
            )
            if path or self.page.web:
                self.notify("Backup criado com sucesso.")

        async def import_csv(e) -> None:
            files = await ft.FilePicker().pick_files(
                allow_multiple=False,
                with_data=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"],
            )
            if not files or not files[0].bytes:
                return
            try:
                rows = parse_csv_bytes(files[0].bytes)
            except Exception as ex:
                self.show_errors([str(ex)])
                return

            imported = 0
            skipped = 0
            for row in rows:
                data = {
                    "matricula": row.get("matricula", ""),
                    "nome": row.get("nome", ""),
                    "email": row.get("email", ""),
                    "telefone": normalize_phone(row.get("telefone", "")),
                    "sexo": row.get("sexo", ""),
                    "data_nascimento": row.get("data_nascimento", ""),
                    "endereco": row.get("endereco", ""),
                    "curso": row.get("curso", ""),
                    "periodo": row.get("periodo") or None,
                    "status": row.get("status") or "Ativo",
                    "foto": "",
                }
                errors = validate_student(data)
                if errors or self.repo.matricula_exists(data["matricula"]):
                    skipped += 1
                    continue
                if data["periodo"] is not None:
                    data["periodo"] = int(data["periodo"])
                try:
                    self.repo.create_student(data)
                    imported += 1
                except sqlite3.IntegrityError:
                    skipped += 1

            self.notify(f"Importação concluída: {imported} importado(s), {skipped} ignorado(s).")
            self.render()

        def action_card(title: str, description: str, icon: str, button: str, handler) -> ft.Container:
            return ft.Container(
                expand=True,
                padding=20,
                bgcolor=SURFACE,
                border=ft.Border.all(1, BORDER),
                border_radius=16,
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Container(
                            width=44,
                            height=44,
                            border_radius=12,
                            bgcolor=INDIGO_SOFT,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(icon, color=INDIGO),
                        ),
                        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.Text(description, size=12, color=TEXT_MUTED),
                        ft.Container(height=4),
                        ft.Button(content=button, icon=icon, on_click=handler),
                    ],
                ),
            )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[
                section_title("Dados e backup", "Importe, exporte e proteja os dados do sistema."),
                ft.Row(
                    spacing=14,
                    controls=[
                        action_card("Exportar CSV", "Gera um arquivo compatível com planilhas e outros sistemas.", ft.Icons.TABLE_VIEW_OUTLINED, "Exportar CSV", export_csv),
                        action_card("Exportar Excel", "Gera uma planilha .xlsx pronta para abrir no Excel.", ft.Icons.GRID_ON_ROUNDED, "Exportar Excel", export_xlsx),
                    ],
                ),
                ft.Row(
                    spacing=14,
                    controls=[
                        action_card("Importar alunos", "Importe vários alunos de uma vez usando o modelo CSV incluído.", ft.Icons.UPLOAD_FILE_ROUNDED, "Importar CSV", import_csv),
                        action_card("Backup do banco", "Salve uma cópia completa do banco SQLite em outro local.", ft.Icons.BACKUP_OUTLINED, "Criar backup", backup),
                    ],
                ),
                ft.Container(
                    padding=18,
                    bgcolor="#FFFBEB",
                    border=ft.Border.all(1, "#FDE68A"),
                    border_radius=14,
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color="#D97706"),
                            ft.Text(
                                "Para importar, use o arquivo modelo_importacao.csv que acompanha o projeto. Matrícula, nome, e-mail e curso são obrigatórios.",
                                color="#92400E",
                                size=12,
                            ),
                        ]
                    ),
                ),
            ],
        )


def main(page: ft.Page):
    AcademicApp(page)


if __name__ == "__main__":
    ft.run(main)
