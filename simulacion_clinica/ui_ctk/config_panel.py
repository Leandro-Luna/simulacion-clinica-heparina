"""Panel de configuración lateral (equivalente al sidebar de Streamlit)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import customtkinter as ctk

from simulacion_clinica.ui.config_state import UIConfigState

_FUENTE = "Segoe UI"


class ConfigPanel(ctk.CTkScrollableFrame):
    """Panel izquierdo con todos los parámetros editables."""

    def __init__(
        self,
        master: Any,
        on_reset: Callable[[], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, width=280, **kwargs)
        self._entries: dict[str, ctk.CTkEntry] = {}
        self._on_reset = on_reset

        ctk.CTkLabel(self, text="Configuración", font=(_FUENTE, 18, "bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )
        ctk.CTkButton(
            self, text="Restaurar defaults", command=self._reset, fg_color="gray40"
        ).pack(fill="x", padx=8, pady=(0, 8))

        self._seccion("Tiempo / aleatoriedad", [
            ("TF (días)", "TF", 365, 1, 1),
            ("N° réplicas", "n_replicas", 100, 1, 1),
            ("Seed (0 = aleatorio)", "seed", 0, 0, 1),
            ("Alpha (IC)", "alpha", 0.05, 0.001, 0.01),
        ])
        self._seccion("Stock", [
            ("Stock inicial", "ST_inicial", 1000, 0, 100),
            ("Compra emergencia (PE)", "PE", 500, 0, 100),
            ("Stock seguridad (SS)", "SS", 300, 0, 100),
            ("Tamaño pedido (TP)", "TP", 2000, 0, 100),
        ])
        self._seccion("Costos", [
            ("Costo unitario pedido", "costo_unitario_pedido", 1150, 0, 50),
            ("Costo unitario emergencia", "costo_unitario_emergencia", 2300, 0, 50),
        ])
        self._seccion("Modelo base (ventana)", [
            ("Día pedido desde", "dia_pedido_desde", 15, 1, 1),
            ("Día pedido hasta", "dia_pedido_hasta", 20, 1, 1),
        ])
        self._seccion("Optimización (grilla PEP × TP)", [
            ("PEP default", "punto_emision_pedido", 2000, 0, 100),
            ("PEP mín", "pep_min", 500, 0, 100),
            ("PEP máx", "pep_max", 4000, 0, 100),
            ("PEP paso", "pep_paso", 500, 1, 100),
            ("TP mín", "tp_min", 500, 0, 100),
            ("TP máx", "tp_max", 4000, 0, 100),
            ("TP paso", "tp_paso", 500, 1, 100),
        ])

    def _seccion(self, titulo: str, campos: list[tuple[str, str, float, float, float]]) -> None:
        ctk.CTkLabel(self, text=titulo, font=(_FUENTE, 13, "bold")).pack(
            anchor="w", padx=8, pady=(12, 2)
        )
        for etiqueta, clave, valor_defecto, _min, _paso in campos:
            ctk.CTkLabel(self, text=etiqueta, font=(_FUENTE, 11)).pack(
                anchor="w", padx=12, pady=(4, 0)
            )
            entry = ctk.CTkEntry(self, width=200)
            entry.insert(0, str(valor_defecto))
            entry.pack(anchor="w", padx=12, pady=(0, 2))
            self._entries[clave] = entry

    def _leer_float(self, clave: str, defecto: float) -> float:
        try:
            return float(self._entries[clave].get())
        except ValueError:
            return defecto

    def _leer_int(self, clave: str, defecto: int) -> int:
        try:
            return int(float(self._entries[clave].get()))
        except ValueError:
            return defecto

    def aplicar_a_state(self, state: UIConfigState) -> None:
        """Lee los entries y actualiza el UIConfigState."""
        state.TF = self._leer_int("TF", 365)
        state.n_replicas = self._leer_int("n_replicas", 100)
        state.alpha = self._leer_float("alpha", 0.05)
        state.ST_inicial = self._leer_int("ST_inicial", 1000)
        state.PE = self._leer_int("PE", 500)
        state.SS = self._leer_int("SS", 300)
        state.TP = self._leer_int("TP", 1500)
        state.costo_unitario_pedido = self._leer_int("costo_unitario_pedido", 1150)
        state.costo_unitario_emergencia = self._leer_int("costo_unitario_emergencia", 2300)
        state.dia_pedido_desde = self._leer_int("dia_pedido_desde", 15)
        state.dia_pedido_hasta = self._leer_int("dia_pedido_hasta", 20)
        state.punto_emision_pedido = self._leer_int("punto_emision_pedido", 2000)
        state.pep_min = self._leer_int("pep_min", 500)
        state.pep_max = self._leer_int("pep_max", 4000)
        state.pep_paso = self._leer_int("pep_paso", 500)
        state.tp_min = self._leer_int("tp_min", 500)
        state.tp_max = self._leer_int("tp_max", 4000)
        state.tp_paso = self._leer_int("tp_paso", 500)
        seed_val = self._leer_int("seed", 0)
        state.seed = seed_val if seed_val > 0 else None

    def _reset(self) -> None:
        defaults = UIConfigState()
        for clave, entry in self._entries.items():
            valor = getattr(defaults, clave, 0)
            if valor is None:
                valor = 0
            entry.delete(0, "end")
            entry.insert(0, str(valor))
        if self._on_reset is not None:
            self._on_reset()
