"""Punto de entrada de la aplicación con Flet.

Por defecto corre en modo web (navegador). Para forzar ventana de escritorio:

    FLET_VIEW=desktop uv run python -m simulacion_clinica.ui.app
"""

from __future__ import annotations

import os

import flet as ft

from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.views.config_view import ConfigView
from simulacion_clinica.ui.views.optimizacion_view import OptimizacionView
from simulacion_clinica.ui.views.simulacion_view import SimulacionView


class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.state = UIConfigState.from_defaults()
        self._setup_page()
        self._build_layout()

    def _setup_page(self) -> None:
        self.page.title = "Simulación de Stock de Heparina"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

    def _build_layout(self) -> None:
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Configuración",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.TRENDING_UP,
                    selected_icon=ft.Icons.TRENDING_UP,
                    label="Simulación",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.AUTO_GRAPH,
                    selected_icon=ft.Icons.AUTO_GRAPH,
                    label="Optimización",
                ),
            ],
            on_change=self._on_nav_change,
        )

        self.content_area = ft.Container(
            content=ConfigView(self),
            expand=True,
            padding=20,
        )

        self.page.add(
            ft.Row(
                [
                    self.navigation_rail,
                    ft.VerticalDivider(width=1),
                    self.content_area,
                ],
                expand=True,
            )
        )

    def _on_nav_change(self, e: ft.ControlEvent) -> None:
        index = self.navigation_rail.selected_index
        if index == 0:
            self.content_area.content = ConfigView(self)
        elif index == 1:
            self.content_area.content = SimulacionView(self)
        elif index == 2:
            self.content_area.content = OptimizacionView(self)
        self.page.update()


def main() -> None:
    view_mode = os.environ.get("FLET_VIEW", "web").lower()
    view = ft.AppView.FLET_APP if view_mode == "desktop" else ft.AppView.WEB_BROWSER
    ft.run(App, view=view)


if __name__ == "__main__":
    main()
