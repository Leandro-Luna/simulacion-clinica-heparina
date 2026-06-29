"""Helpers para mostrar DataFrames de pandas en ttk.Treeview."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import pandas as pd

_FUENTE = "Segoe UI"


def mostrar_dataframe(
    parent: tk.Widget,
    df: pd.DataFrame,
    height: int = 400,
    max_col_width: int = 180,
) -> ttk.Treeview:
    """Crea un Treeview con scroll que muestra el DataFrame."""
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=4, pady=4)

    cols = list(df.columns)
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=height // 20)

    for col in cols:
        tree.heading(col, text=col)
        ancho = min(max(len(str(col)) * 9, 70), max_col_width)
        tree.column(col, width=ancho, anchor="center", minwidth=50)

    for _, fila in df.iterrows():
        valores = [_formato_celda(v) for v in fila]
        tree.insert("", "end", values=valores)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    return tree


def _formato_celda(valor: object) -> str:
    """Formatea un valor para mostrar en Treeview."""
    if isinstance(valor, float):
        return f"{valor:,.2f}"
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return str(valor)
