"""Aplicación principal con CustomTkinter.

Ejecutar:

    uv run python -m simulacion_clinica.ui_ctk.app
"""

from __future__ import annotations

import sys

# Activar DPI awareness en Windows ANTES de crear la ventana
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# Backend matplotlib ANTES de importar pyplot
import matplotlib  # noqa: E402

matplotlib.use("TkAgg")  # noqa: E402

from tkinter import ttk

import customtkinter as ctk

from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui_ctk.config_panel import ConfigPanel
from simulacion_clinica.ui_ctk.optimizacion_tab import OptimizacionTab
from simulacion_clinica.ui_ctk.simulacion_tab import SimulacionTab

_FUENTE = "Segoe UI"


def _configurar_ttk_estilo() -> None:
    """Aplica un estilo oscuro moderno a los Treeview (ttk)."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background="#2b2b2b",
        foreground="#ffffff",
        fieldbackground="#2b2b2b",
        borderwidth=0,
        font=(_FUENTE, 11),
        rowheight=26,
    )
    style.configure(
        "Treeview.Heading",
        background="#1f6aa5",
        foreground="#ffffff",
        font=(_FUENTE, 11, "bold"),
        borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", "#1f6aa5")],
        foreground=[("selected", "#ffffff")],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", "#144870")],
    )
    style.configure("Vertical.TScrollbar", background="#333333", troughcolor="#1e1e1e")
    style.configure("Horizontal.TScrollbar", background="#333333", troughcolor="#1e1e1e")


class App(ctk.CTk):
    """Ventana principal de la aplicación."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Simulación de Stock de Heparina — Centro de Diálisis")
        self.geometry("1200x800")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)

        _configurar_ttk_estilo()

        self._state = UIConfigState.from_defaults()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._panel = ConfigPanel(self, on_reset=self._on_reset)
        self._panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4), pady=4)
        self._panel.aplicar_a_state(self._state)

        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew", pady=4)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            right,
            text="Simulación de Stock de Heparina",
            font=(_FUENTE, 20, "bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))

        tabs = ctk.CTkTabview(right)
        tabs.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        tabs.add("Simulación")
        tabs.add("Optimización")

        self._sim_tab = SimulacionTab(tabs.tab("Simulación"))
        self._sim_tab.set_state(self._state)
        self._sim_tab.pack(fill="both", expand=True)

        self._opt_tab = OptimizacionTab(tabs.tab("Optimización"))
        self._opt_tab.set_state(self._state)
        self._opt_tab.pack(fill="both", expand=True)

    def _on_reset(self) -> None:
        self._state = UIConfigState.from_defaults()
        self._sim_tab.set_state(self._state)
        self._opt_tab.set_state(self._state)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
