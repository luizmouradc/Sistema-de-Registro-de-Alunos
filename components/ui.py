from __future__ import annotations

import flet as ft

from config import (
    BORDER, DANGER, DANGER_SOFT, INDIGO, INDIGO_SOFT, INFO, INFO_SOFT,
    SUCCESS, SUCCESS_SOFT, SURFACE, TEXT, TEXT_MUTED, WARNING, WARNING_SOFT,
)


def section_title(title: str, subtitle: str = "") -> ft.Column:
    controls: list[ft.Control] = [
        ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=TEXT),
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=14, color=TEXT_MUTED))
    return ft.Column(spacing=4, controls=controls)


def stat_card(title: str, value: str, icon: str, color: str = INDIGO, soft: str = INDIGO_SOFT) -> ft.Container:
    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=16,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(title, size=13, color=TEXT_MUTED),
                        ft.Text(value, size=30, weight=ft.FontWeight.BOLD, color=TEXT),
                    ],
                ),
                ft.Container(
                    width=48,
                    height=48,
                    border_radius=14,
                    bgcolor=soft,
                    content=ft.Icon(icon, color=color, size=24),
                    alignment=ft.Alignment.CENTER,
                ),
            ],
        ),
    )


def status_badge(status: str) -> ft.Container:
    mapping = {
        "Ativo": (SUCCESS, SUCCESS_SOFT),
        "Trancado": (WARNING, WARNING_SOFT),
        "Formado": (INFO, INFO_SOFT),
        "Inativo": (DANGER, DANGER_SOFT),
    }
    color, bg = mapping.get(status, (TEXT_MUTED, "#F3F4F6"))
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
        bgcolor=bg,
        border_radius=999,
        content=ft.Text(status or "-", size=12, weight=ft.FontWeight.W_600, color=color),
    )


def empty_state(icon: str, title: str, subtitle: str) -> ft.Container:
    return ft.Container(
        padding=40,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Icon(icon, size=46, color="#9CA3AF"),
                ft.Text(title, size=17, weight=ft.FontWeight.W_600, color=TEXT),
                ft.Text(subtitle, size=13, color=TEXT_MUTED, text_align=ft.TextAlign.CENTER),
            ],
        ),
    )
