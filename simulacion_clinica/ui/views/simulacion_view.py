"""Vista de simulación base."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft
import pandas as pd

from simulacion_clinica.simulacion import simular_replicas
from simulacion_clinica.ui.components.charts import (
    chart_costo_acumulado,
    chart_demanda_vs_dia,
    chart_replicas_ctf,
    chart_stock_vs_dia,
)
from simulacion_clinica.ui.components.data_table import dataframe_to_datatable
from simulacion_clinica.ui.utils import exportar_simulacion

if TYPE_CHECKING:
    from simulacion_clinica.ui.app import App


class SimulacionView(ft.Column):
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
                ft.Text("Simulación base", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Ejecutar simulación",
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
        self.df_corrida1: pd.DataFrame | None = None
        self.df_resumen: pd.DataFrame | None = None

    def _ejecutar(self, e: ft.ControlEvent) -> None:
        self._boton_exportar.disabled = True
        self._resultado_container.controls.clear()
        self._resultado_container.controls.append(
            ft.Row([ft.ProgressRing(), ft.Text("Ejecutando simulación...")])
        )
        self.app.page.update()

        cfg = self.app.state.to_config()
        self.df_corrida1, self.df_resumen = simular_replicas(cfg)

        self._resultado_container.controls.clear()

        # KPIs
        ultima_fila = self.df_corrida1.iloc[-1]
        self._resultado_container.controls.append(
            ft.Row(
                [
                    self._kpi_card("CTF final", f"${ultima_fila['costo_total_acum']:,.0f}"),
                    self._kpi_card(
                        "Pedidos", f"{int(self.df_resumen['n_pedidos'].iloc[0])}"
                    ),
                    self._kpi_card(
                        "Emergencias", f"{int(self.df_resumen['n_emergencias'].iloc[0])}"
                    ),
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
                        text="Stock",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_stock_vs_dia(self.df_corrida1),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Tab(
                        text="Costo acumulado",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_costo_acumulado(self.df_corrida1),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Tab(
                        text="Demanda",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_demanda_vs_dia(self.df_corrida1),
                                    width=800,
                                )
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Tab(
                        text="CTF por réplica",
                        content=ft.Column(
                            [
                                ft.Image(
                                    src_base64=chart_replicas_ctf(self.df_resumen),
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
                title=ft.Text("Detalle por día (Corrida 1)"),
                controls=[
                    ft.Column(
                        [dataframe_to_datatable(self.df_corrida1)],
                        scroll=ft.ScrollMode.AUTO,
                    )
                ],
            )
        )
        self._resultado_container.controls.append(
            ft.ExpansionTile(
                title=ft.Text("Resumen de réplicas"),
                controls=[
                    ft.Column(
                        [dataframe_to_datatable(self.df_resumen)],
                        scroll=ft.ScrollMode.AUTO,
                    )
                ],
            )
        )

        self._boton_exportar.disabled = False
        self.app.page.update()

    def _exportar(self, e: ft.ControlEvent) -> None:
        if self.df_corrida1 is None or self.df_resumen is None:
            return
        ruta = exportar_simulacion(self.df_corrida1, self.df_resumen)
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
