"""Tab de optimización por punto de emisión."""

from __future__ import annotations

import threading
from tkinter import filedialog
from typing import Any

import customtkinter as ctk
import pandas as pd

from simulacion_clinica.optimizacion import optimizar, simular_optimizacion
from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.utils import exportar_optimizacion_bytes
from simulacion_clinica.ui_ctk.charts import (
    chart_optimizacion_ctf,
    chart_optimizacion_mejor_detalle,
    embed_chart,
)
from simulacion_clinica.ui_ctk.tablas import mostrar_dataframe

_FUENTE = "Segoe UI"


class OptimizacionTab(ctk.CTkFrame):
    """Tab de optimización con progress bar, métricas y tablas."""

    def __init__(self, master: Any) -> None:
        super().__init__(master)
        self._df_resultados: pd.DataFrame | None = None
        self._df_mejor: pd.DataFrame | None = None

        ctk.CTkLabel(self, text="Optimización", font=(_FUENTE, 16, "bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=4)
        ctk.CTkButton(btn_frame, text="Ejecutar optimización", command=self._ejecutar).pack(
            side="left"
        )
        self._btn_exportar = ctk.CTkButton(
            btn_frame, text="Exportar a Excel", command=self._exportar, state="disabled"
        )
        self._btn_exportar.pack(side="left", padx=8)

        self._lbl_status = ctk.CTkLabel(self, text="", font=(_FUENTE, 12))
        self._lbl_status.pack(anchor="w", padx=8, pady=2)

        self._progress = ctk.CTkProgressBar(self, width=400)
        self._progress.pack(anchor="w", padx=8, pady=2)
        self._progress.set(0)

        self._metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._metrics_frame.pack(fill="x", padx=8, pady=4)

        self._tabs = ctk.CTkTabview(self)
        self._tabs.pack(fill="both", expand=True, padx=8, pady=4)
        self._tabs.add("Gráficos")
        self._tabs.add("Combinaciones evaluadas")
        self._tabs.add("Detalle mejor combinación")

    def set_state(self, state: UIConfigState) -> None:
        self._state = state

    def _ejecutar(self) -> None:
        self._btn_exportar.configure(state="disabled")
        self._progress.set(0)
        self._lbl_status.configure(text="Preparando optimización...")
        threading.Thread(target=self._run_optimizacion, daemon=True).start()

    def _on_combo_done(self, completados: int, total: int) -> None:
        """Callback llamado desde el hilo de optimización."""
        self.after(0, self._actualizar_progress, completados, total)

    def _actualizar_progress(self, completados: int, total: int) -> None:
        self._progress.set(completados / total)
        self._lbl_status.configure(text=f"Optimizando {completados}/{total} combinaciones...")

    def _run_optimizacion(self) -> None:
        cfg = self._state.to_config_optimizacion()
        puntos = list(range(self._state.pep_min, self._state.pep_max + 1, self._state.pep_paso))
        tamanios = list(range(self._state.tp_min, self._state.tp_max + 1, self._state.tp_paso))

        df_resultados = optimizar(cfg, puntos, tamanios, on_combo_done=self._on_combo_done)

        mejor = df_resultados.iloc[0]
        cfg_mejor = self._state.to_config_optimizacion()
        cfg_mejor.TP = int(mejor["tamaño_pedido"])
        cfg_mejor.punto_emision_pedido = int(mejor["punto_emision_pedido"])
        cfg_mejor.seed = None
        df_mejor, _ = simular_optimizacion(cfg_mejor)

        self._df_resultados = df_resultados
        self._df_mejor = df_mejor
        self.after(0, self._mostrar_resultados)

    def _mostrar_resultados(self) -> None:
        assert self._df_resultados is not None
        assert self._df_mejor is not None

        mejor = self._df_resultados.iloc[0]
        total = len(self._df_resultados)
        self._progress.set(1.0)
        self._lbl_status.configure(
            text=f"Completado — {total} combinaciones evaluadas"
        )
        self._btn_exportar.configure(state="normal")

        for w in self._metrics_frame.winfo_children():
            w.destroy()
        for clave, etiqueta in [
            ("punto_emision_pedido", "Mejor PEP"),
            ("tamaño_pedido", "Mejor TP"),
            ("CTF_promedio", "CTF promedio"),
            ("IC_inf", "IC Inf"),
            ("IC_sup", "IC Sup"),
        ]:
            valor = mejor[clave]
            texto = f"${valor:,.0f}" if "CTF" in clave or "IC" in clave else f"{int(valor)}"
            ctk.CTkLabel(
                self._metrics_frame,
                text=f"{etiqueta}\n{texto}",
                font=(_FUENTE, 11),
                justify="center",
            ).pack(side="left", padx=12)

        for _tab_name, frame, df in [
            (
                "Combinaciones evaluadas",
                self._tabs.tab("Combinaciones evaluadas"),
                self._df_resultados,
            ),
            (
                "Detalle mejor combinación",
                self._tabs.tab("Detalle mejor combinación"),
                self._df_mejor,
            ),
        ]:
            for w in frame.winfo_children():
                w.destroy()
            mostrar_dataframe(frame, df, height=400)

        # Gráficos
        graficos_frame = self._tabs.tab("Gráficos")
        for w in graficos_frame.winfo_children():
            w.destroy()

        grid = ctk.CTkFrame(graficos_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=4, pady=4)
        grid.grid_columnconfigure((0, 1), weight=1)
        grid.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(grid)
        left.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        embed_chart(left, chart_optimizacion_ctf(self._df_resultados, top_n=10))

        right = ctk.CTkFrame(grid)
        right.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        embed_chart(right, chart_optimizacion_mejor_detalle(self._df_mejor))

    def _exportar(self) -> None:
        if self._df_resultados is None or self._df_mejor is None:
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            initialfile="resultado_optimizacion.xlsx",
        )
        if ruta:
            bytes_excel = exportar_optimizacion_bytes(self._df_resultados, self._df_mejor)
            with open(ruta, "wb") as f:
                f.write(bytes_excel)
            self._lbl_status.configure(text=f"Exportado a {ruta}")
