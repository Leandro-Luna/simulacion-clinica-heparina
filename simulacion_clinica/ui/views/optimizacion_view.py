"""Vista de optimización por punto de emisión."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from simulacion_clinica.optimizacion import optimizar, simular_optimizacion
from simulacion_clinica.ui.components.charts import (
    chart_costo_acumulado,
    chart_optimizacion_ctf,
    chart_stock_vs_dia,
)
from simulacion_clinica.ui.components.data_table import dataframe_to_datatable
from simulacion_clinica.ui.utils import exportar_optimizacion

if TYPE_CHECKING:
    from simulacion_clinica.ui.app import App


class OptimizacionView(ft.Column):
    def __init__(self, app: App) -> None:
        self.app = app
        self._resultado_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self._boton_exportar = ft.ElevatedButton(
            "Exportar a Excel",
            icon=ft.Icons.DOWNLOAD,
            on_click=self._exportar,
            disabled=True,
        )
        super().__init__(
            controls=[
                ft.Text("Optimización", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Ejecutar optimización",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=self._ejecutar,
                        ),
                        self._boton_exportar,
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                self._resultado_container,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self.df_resultados: pd.DataFrame | None = None
        self.df_mejor: pd.DataFrame | None = None

    def _ejecutar(self, e: ft.ControlEvent) -> None:
        self._boton_exportar.disabled = True
        self._resultado_container.controls.clear()
        self._resultado_container.controls.append(
            ft.Row([ft.ProgressRing(), ft.Text("Ejecutando optimización...")])
        )
        self.app.page.update()

        state = self.app.state
        cfg = state.to_config_optimizacion()
        puntos_emision = list(range(state.pep_min, state.pep_max + 1, state.pep_paso))
        tamanios_pedido = list(range(state.tp_min, state.tp_max + 1, state.tp_paso))

        self.df_resultados = optimizar(cfg, puntos_emision, tamanios_pedido)
        mejor = self.df_resultados.iloc[0]
        cfg_mejor = state.to_config_optimizacion()
        cfg_mejor.TP = int(mejor["tamaño_pedido"])
        cfg_mejor.punto_emision_pedido = int(mejor["punto_emision_pedido"])
        cfg_mejor.seed = None
        self.df_mejor, _ = simular_optimizacion(cfg_mejor)

        self._resultado_container.controls.clear()

        # KPIs
        self._resultado_container.controls.append(
            ft.Row(
                [
                    self._kpi_card("Mejor PEP", f"{int(mejor['punto_emision_pedido'])}"),
                    self._kpi_card("Mejor TP", f"{int(mejor['tamaño_pedido'])}"),
                    self._kpi_card("CTF promedio", f"${mejor['CTF_promedio']:,.0f}"),
                ],
                spacing=20,
            )
        )

        # Gráficos
        self._resultado_container.controls.append(
            ft.Tabs(
                selected_index=0,
                tabs=[
                    ft.Tab(
                        text="Ranking combinaciones",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_optimizacion_ctf(self.df_resultados, top_n=10),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Tab(
                        text="Stock mejor combinación",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_stock_vs_dia(self.df_mejor),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Tab(
                        text="Costo mejor combinación",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_costo_acumulado(self.df_mejor),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                ],
                expand=True,
            )
        )

        # Tablas
        self._resultado_container.controls.append(
            ft.ExpansionTile(
                title=ft.Text("Combinaciones evaluadas"),
                controls=[
                    ft.Column(
                        [dataframe_to_datatable(self.df_resultados)],
                        scroll=ft.ScrollMode.AUTO,
                    )
                ],
            )
        )
        self._resultado_container.controls.append(
            ft.ExpansionTile(
                title=ft.Text("Detalle mejor combinación"),
                controls=[
                    ft.Column(
                        [dataframe_to_datatable(self.df_mejor)],
                        scroll=ft.ScrollMode.AUTO,
                    )
                ],
            )
        )

        self._boton_exportar.disabled = False
        self.app.page.update()

    def _exportar(self, e: ft.ControlEvent) -> None:
        if self.df_resultados is None or self.df_mejor is None:
            return
        ruta = exportar_optimizacion(self.df_resultados, self.df_mejor)
        self.app.page.open(
            ft.SnackBar(
                content=ft.Text(f"Exportado a {ruta}"),
                action="Abrir",
                on_action=lambda _: self.app.page.launch_url(f"file://{ruta}"),
            )
        )

    @staticmethod
    def _kpi_card(titulo: str, valor: str) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(titulo, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text(valor, size=22, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=16,
                width=150,
            )
        )
