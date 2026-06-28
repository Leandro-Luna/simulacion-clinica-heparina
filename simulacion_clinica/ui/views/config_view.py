"""Vista de configuración de parámetros."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from simulacion_clinica.ui.app import App


class ConfigView(ft.Column):
    def __init__(self, app: App) -> None:
        super().__init__(controls=self._build_controls(), scroll=ft.ScrollMode.AUTO, expand=True)
        self.app = app

    def _field(
        self,
        label: str,
        value: int | float | str | None,
        on_change: Callable[[ft.ControlEvent], None],
        keyboard_type: ft.KeyboardType = ft.KeyboardType.NUMBER,
        hint: str | None = None,
    ) -> ft.TextField:
        return ft.TextField(
            label=label,
            value=str(value) if value is not None else "",
            keyboard_type=keyboard_type,
            on_change=on_change,
            hint_text=hint,
            width=200,
        )

    def _build_controls(self) -> list[ft.Control]:
        state = self.app.state

        # Tiempo
        self.tf_field = self._field("TF (días)", state.TF, self._on_tf_change)
        self.n_replicas_field = self._field(
            "N° réplicas", state.n_replicas, self._on_n_replicas_change
        )
        self.seed_field = self._field(
            "Seed (vacío = aleatorio)",
            state.seed,
            self._on_seed_change,
            hint="None",
        )
        self.alpha_field = self._field("Alpha (IC)", state.alpha, self._on_alpha_change)

        # Stock
        self.st_inicial_field = self._field(
            "Stock inicial", state.ST_inicial, self._on_st_inicial_change
        )
        self.pe_field = self._field("Compra emergencia (PE)", state.PE, self._on_pe_change)
        self.ss_field = self._field("Stock seguridad (SS)", state.SS, self._on_ss_change)
        self.tp_field = self._field("Tamaño pedido (TP)", state.TP, self._on_tp_change)

        # Costos
        self.costo_pedido_field = self._field(
            "Costo unitario pedido", state.costo_unitario_pedido, self._on_costo_pedido_change
        )
        self.costo_emerg_field = self._field(
            "Costo unitario emergencia",
            state.costo_unitario_emergencia,
            self._on_costo_emerg_change,
        )

        # Ventana de pedido
        self.dia_desde_field = self._field(
            "Día pedido desde", state.dia_pedido_desde, self._on_dia_desde_change
        )
        self.dia_hasta_field = self._field(
            "Día pedido hasta", state.dia_pedido_hasta, self._on_dia_hasta_change
        )

        # Optimización
        self.pep_field = self._field("PEP default", state.punto_emision_pedido, self._on_pep_change)
        self.pep_min_field = self._field("PEP mín", state.pep_min, self._on_pep_min_change)
        self.pep_max_field = self._field("PEP máx", state.pep_max, self._on_pep_max_change)
        self.pep_paso_field = self._field("PEP paso", state.pep_paso, self._on_pep_paso_change)
        self.tp_min_field = self._field("TP mín", state.tp_min, self._on_tp_min_change)
        self.tp_max_field = self._field("TP máx", state.tp_max, self._on_tp_max_change)
        self.tp_paso_field = self._field("TP paso", state.tp_paso, self._on_tp_paso_change)

        return [
            ft.Text("Configuración", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text("Tiempo / aleatoriedad", weight=ft.FontWeight.BOLD),
                            self.tf_field,
                            self.n_replicas_field,
                            self.seed_field,
                            self.alpha_field,
                        ],
                        spacing=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Stock", weight=ft.FontWeight.BOLD),
                            self.st_inicial_field,
                            self.pe_field,
                            self.ss_field,
                            self.tp_field,
                        ],
                        spacing=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Costos", weight=ft.FontWeight.BOLD),
                            self.costo_pedido_field,
                            self.costo_emerg_field,
                        ],
                        spacing=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Modelo base", weight=ft.FontWeight.BOLD),
                            self.dia_desde_field,
                            self.dia_hasta_field,
                        ],
                        spacing=10,
                    ),
                    ft.Column(
                        [
                            ft.Text("Optimización", weight=ft.FontWeight.BOLD),
                            self.pep_field,
                            self.pep_min_field,
                            self.pep_max_field,
                            self.pep_paso_field,
                            self.tp_min_field,
                            self.tp_max_field,
                            self.tp_paso_field,
                        ],
                        spacing=10,
                    ),
                ],
                spacing=30,
                wrap=True,
            ),
            ft.Divider(),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Restaurar defaults",
                        icon=ft.Icons.RESTORE,
                        on_click=self._reset,
                    ),
                ]
            ),
        ]

    # Event handlers
    def _on_tf_change(self, e: ft.ControlEvent) -> None:
        self.app.state.TF = self._parse_int(e.data)

    def _on_n_replicas_change(self, e: ft.ControlEvent) -> None:
        self.app.state.n_replicas = self._parse_int(e.data)

    def _on_seed_change(self, e: ft.ControlEvent) -> None:
        text = e.data.strip()
        self.app.state.seed = self._parse_optional_int(text)

    def _on_alpha_change(self, e: ft.ControlEvent) -> None:
        self.app.state.alpha = self._parse_float(e.data)

    def _on_st_inicial_change(self, e: ft.ControlEvent) -> None:
        self.app.state.ST_inicial = self._parse_int(e.data)

    def _on_pe_change(self, e: ft.ControlEvent) -> None:
        self.app.state.PE = self._parse_int(e.data)

    def _on_ss_change(self, e: ft.ControlEvent) -> None:
        self.app.state.SS = self._parse_int(e.data)

    def _on_tp_change(self, e: ft.ControlEvent) -> None:
        self.app.state.TP = self._parse_int(e.data)

    def _on_costo_pedido_change(self, e: ft.ControlEvent) -> None:
        self.app.state.costo_unitario_pedido = self._parse_int(e.data)

    def _on_costo_emerg_change(self, e: ft.ControlEvent) -> None:
        self.app.state.costo_unitario_emergencia = self._parse_int(e.data)

    def _on_dia_desde_change(self, e: ft.ControlEvent) -> None:
        self.app.state.dia_pedido_desde = self._parse_int(e.data)

    def _on_dia_hasta_change(self, e: ft.ControlEvent) -> None:
        self.app.state.dia_pedido_hasta = self._parse_int(e.data)

    def _on_pep_change(self, e: ft.ControlEvent) -> None:
        self.app.state.punto_emision_pedido = self._parse_int(e.data)

    def _on_pep_min_change(self, e: ft.ControlEvent) -> None:
        self.app.state.pep_min = self._parse_int(e.data)

    def _on_pep_max_change(self, e: ft.ControlEvent) -> None:
        self.app.state.pep_max = self._parse_int(e.data)

    def _on_pep_paso_change(self, e: ft.ControlEvent) -> None:
        self.app.state.pep_paso = self._parse_int(e.data)

    def _on_tp_min_change(self, e: ft.ControlEvent) -> None:
        self.app.state.tp_min = self._parse_int(e.data)

    def _on_tp_max_change(self, e: ft.ControlEvent) -> None:
        self.app.state.tp_max = self._parse_int(e.data)

    def _on_tp_paso_change(self, e: ft.ControlEvent) -> None:
        self.app.state.tp_paso = self._parse_int(e.data)

    def _reset(self, e: ft.ControlEvent) -> None:
        self.app.state.reset()
        self.app.page.views.clear()
        self.app.page.views.append(ConfigView(self.app))
        self.app.page.update()

    @staticmethod
    def _parse_int(value: str) -> int:
        try:
            return int(value)
        except ValueError:
            return 0

    @staticmethod
    def _parse_optional_int(value: str) -> int | None:
        if value == "" or value.lower() in ("none", "null"):
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_float(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            return 0.05
