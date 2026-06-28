"""Gráficos reutilizables para la UI usando matplotlib."""

from __future__ import annotations

import base64
import io

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")


def _figure_to_image(figure: plt.Figure) -> str:
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight", dpi=120)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def chart_stock_vs_dia(df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["dia"], df["stock_final"], color="steelblue", linewidth=1.2)
    ax.axhline(df["stock_final"].mean(), color="gray", linestyle="--", alpha=0.7)
    ax.set_title("Evolución del stock final por día")
    ax.set_xlabel("Día")
    ax.set_ylabel("Stock (cc)")
    ax.grid(True, alpha=0.3)
    data = _figure_to_image(fig)
    plt.close(fig)
    return data


def chart_costo_acumulado(df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["dia"], df["costo_total_acum"], color="darkred", linewidth=1.5)
    ax.set_title("Costo total acumulado por día")
    ax.set_xlabel("Día")
    ax.set_ylabel("Costo ($)")
    ax.grid(True, alpha=0.3)
    data = _figure_to_image(fig)
    plt.close(fig)
    return data


def chart_demanda_vs_dia(df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#2ca02c" if d > 0 else "#d62728" for d in df["demanda_cc"]]
    ax.bar(df["dia"], df["demanda_cc"], color=colors, width=0.8)
    ax.set_title("Demanda diaria de Heparina")
    ax.set_xlabel("Día")
    ax.set_ylabel("Demanda (cc)")
    ax.grid(True, alpha=0.3, axis="y")
    data = _figure_to_image(fig)
    plt.close(fig)
    return data


def chart_optimizacion_ctf(df: pd.DataFrame, top_n: int = 10) -> bytes:
    df_plot = df.nsmallest(top_n, "CTF_promedio").copy()
    df_plot["combinacion"] = (
        df_plot["punto_emision_pedido"].astype(str)
        + " / "
        + df_plot["tamaño_pedido"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(df_plot["combinacion"], df_plot["CTF_promedio"], color="teal")
    ax.invert_yaxis()
    ax.set_title(f"Top {top_n} combinaciones por CTF promedio")
    ax.set_xlabel("CTF promedio ($)")
    ax.grid(True, alpha=0.3, axis="x")

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.0f}",
            va="center",
            ha="left",
            fontsize=8,
        )

    data = _figure_to_image(fig)
    plt.close(fig)
    return data


def chart_optimizacion_mejor_detalle(df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["dia"], df["stock_final"], color="steelblue", linewidth=1.2)
    ax.set_title("Mejor combinación: evolución del stock")
    ax.set_xlabel("Día")
    ax.set_ylabel("Stock (cc)")
    ax.grid(True, alpha=0.3)
    data = _figure_to_image(fig)
    plt.close(fig)
    return data


def chart_replicas_ctf(df: pd.DataFrame) -> bytes:
    replicas = df[df["replica"].apply(lambda x: isinstance(x, int))]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(replicas["replica"], replicas["CTF"], color="coral")
    ax.set_title("CTF por réplica")
    ax.set_xlabel("Réplica")
    ax.set_ylabel("CTF ($)")
    ax.grid(True, alpha=0.3, axis="y")
    data = _figure_to_image(fig)
    plt.close(fig)
    return data
