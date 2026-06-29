"""Gráficos con matplotlib embebidos en CustomTkinter."""

from __future__ import annotations

import tkinter as tk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

_COLORES = {
    "stock": "steelblue",
    "costo": "darkred",
    "demanda": "#2ca02c",
    "ctf_replica": "coral",
    "ranking": "teal",
}

_TEMA = {
    "figure.facecolor": "#2b2b2b",
    "axes.facecolor": "#2b2b2b",
    "axes.edgecolor": "#555555",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "#3a3a3a",
    "figure.figsize": (7, 3),
    "figure.dpi": 100,
}


def _aplicar_tema() -> None:
    plt.rcParams.update(_TEMA)  # type: ignore[arg-type]


_aplicar_tema()


def embed_chart(parent: tk.Widget, fig: Figure) -> FigureCanvasTkAgg:
    """Embebe una Figure de matplotlib en un frame de tkinter."""
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.pack(fill="both", expand=True, padx=4, pady=4)
    return canvas


def chart_stock_vs_dia(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots()
    ax.plot(df["dia"], df["stock_final"], color=_COLORES["stock"], linewidth=1.2)
    ax.set_title("Evolución del stock final por día")
    ax.set_xlabel("Día")
    ax.set_ylabel("Stock (cc)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def chart_costo_acumulado(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots()
    ax.plot(df["dia"], df["costo_total_acum"], color=_COLORES["costo"], linewidth=1.2)
    ax.set_title("Costo total acumulado por día")
    ax.set_xlabel("Día")
    ax.set_ylabel("Costo ($)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def chart_demanda_vs_dia(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots()
    ax.bar(df["dia"], df["demanda_cc"], color=_COLORES["demanda"], width=1.0)
    ax.set_title("Demanda diaria de Heparina")
    ax.set_xlabel("Día")
    ax.set_ylabel("Demanda (cc)")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def chart_replicas_ctf(df: pd.DataFrame) -> Figure:
    replicas = df[df["replica"].apply(lambda x: isinstance(x, int))].copy()
    fig, ax = plt.subplots()
    ax.bar(replicas["replica"].astype(int), replicas["CTF"], color=_COLORES["ctf_replica"])
    ax.set_title("CTF por réplica")
    ax.set_xlabel("Réplica")
    ax.set_ylabel("CTF ($)")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def chart_optimizacion_ctf(df: pd.DataFrame, top_n: int = 10) -> Figure:
    df_plot = df.nsmallest(top_n, "CTF_promedio").copy()
    df_plot["combinacion"] = (
        df_plot["punto_emision_pedido"].astype(str)
        + " / "
        + df_plot["tamaño_pedido"].astype(str)
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(
        df_plot["combinacion"],
        df_plot["CTF_promedio"],
        color=_COLORES["ranking"],
    )
    ax.bar_label(bars, fmt="$%,.0f", padding=4, color="white", fontsize=9)
    ax.set_title(f"Top {top_n} combinaciones por CTF promedio (menor a mayor)")
    ax.set_xlabel("CTF promedio ($)")
    ax.set_ylabel("PEP / TP")
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis="x")
    fig.tight_layout()
    return fig


def chart_optimizacion_mejor_detalle(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots()
    ax.plot(df["dia"], df["stock_final"], color=_COLORES["stock"], linewidth=1.2)
    ax.set_title("Mejor combinación: evolución del stock")
    ax.set_xlabel("Día")
    ax.set_ylabel("Stock (cc)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
