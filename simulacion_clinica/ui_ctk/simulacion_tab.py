"""Tab de simulación base."""

from __future__ import annotations

import threading
from tkinter import filedialog
from typing import Any

import customtkinter as ctk
import pandas as pd

from simulacion_clinica.simulacion import simular_replicas
from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.utils import exportar_simulacion_bytes
from simulacion_clinica.ui_ctk.tablas import mostrar_dataframe

_ETIQUETAS_STATS = {"Promedio", "Desvío", "Mín", "Máx", "IC Inf", "IC Sup"}
_FUENTE = "Segoe UI"


def _split_resumen(df_resumen: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    mascara = df_resumen["replica"].isin(list(_ETIQUETAS_STATS))
    df_stats: pd.DataFrame = df_resumen[mascara]  # type: ignore[assignment]
    df_replicas: pd.DataFrame = df_resumen[~mascara]  # type: ignore[assignment]
    stats: dict[str, float] = {}
    for _, fila in df_stats.iterrows():
        stats[str(fila["replica"])] = float(fila["CTF"])  # type: ignore[arg-type]
    return df_replicas, stats


class SimulacionTab(ctk.CTkFrame):
    """Tab de simulación base con métricas, tablas y exportación."""

    def __init__(self, master: Any) -> None:
        super().__init__(master)
        self._df_corrida1: pd.DataFrame | None = None
        self._df_resumen: pd.DataFrame | None = None

        ctk.CTkLabel(self, text="Simulación base", font=(_FUENTE, 16, "bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=4)
        ctk.CTkButton(btn_frame, text="Ejecutar simulación", command=self._ejecutar).pack(
            side="left"
        )
        self._btn_exportar = ctk.CTkButton(
            btn_frame, text="Exportar a Excel", command=self._exportar, state="disabled"
        )
        self._btn_exportar.pack(side="left", padx=8)

        self._lbl_status = ctk.CTkLabel(self, text="", font=(_FUENTE, 12))
        self._lbl_status.pack(anchor="w", padx=8, pady=2)

        self._metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._metrics_frame.pack(fill="x", padx=8, pady=4)

        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=8, pady=4)
        self._tabs.add("Detalle por día")
        self._tabs.add("Resumen réplicas")

    def set_state(self, state: UIConfigState) -> None:
        self._state = state

    def _ejecutar(self) -> None:
        self._lbl_status.configure(text="Ejecutando simulación...")
        threading.Thread(target=self._run_simulacion, daemon=True).start()

    def _run_simulacion(self) -> None:
        cfg = self._state.to_config()
        df_corrida1, df_resumen = simular_replicas(cfg)
        self._df_corrida1 = df_corrida1
        self._df_resumen = df_resumen
        self.after(0, self._mostrar_resultados)

    def _mostrar_resultados(self) -> None:
        assert self._df_corrida1 is not None
        assert self._df_resumen is not None

        df_replicas, stats = _split_resumen(self._df_resumen)
        self._lbl_status.configure(
            text=f"Completado — CTF promedio: ${stats.get('Promedio', 0):,.0f}"
        )
        self._btn_exportar.configure(state="normal")

        for w in self._metrics_frame.winfo_children():
            w.destroy()
        for clave, etiqueta in [
            ("Promedio", "CTF promedio"),
            ("Desvío", "Desvío"),
            ("Mín", "Mín"),
            ("IC Inf", "IC Inf"),
            ("IC Sup", "IC Sup"),
        ]:
            ctk.CTkLabel(
                self._metrics_frame,
                text=f"{etiqueta}\n${stats.get(clave, 0):,.0f}",
                font=(_FUENTE, 11),
                justify="center",
            ).pack(side="left", padx=12)

        for tab_name, frame in [
            ("Detalle por día", self._tabs.tab("Detalle por día")),
            ("Resumen réplicas", self._tabs.tab("Resumen réplicas")),
        ]:
            for w in frame.winfo_children():
                w.destroy()
            if tab_name == "Detalle por día":
                mostrar_dataframe(frame, self._df_corrida1, height=400)
            else:
                mostrar_dataframe(frame, df_replicas, height=300)

    def _exportar(self) -> None:
        if self._df_corrida1 is None or self._df_resumen is None:
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="resultado_simulacion.xlsx",
        )
        if ruta:
            bytes_excel = exportar_simulacion_bytes(self._df_corrida1, self._df_resumen)
            with open(ruta, "wb") as f:
                f.write(bytes_excel)
            self._lbl_status.configure(text=f"Exportado a {ruta}")
