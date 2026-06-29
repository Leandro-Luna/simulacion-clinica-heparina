"""Gráficos interactivos para la UI usando Plotly."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def chart_stock_vs_dia(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df, x="dia", y="stock_final", title="Evolución del stock final por día"
    )
    fig.update_layout(xaxis_title="Día", yaxis_title="Stock (cc)", height=350)
    fig.update_traces(line_color="steelblue")
    return fig


def chart_costo_acumulado(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df, x="dia", y="costo_total_acum", title="Costo total acumulado por día"
    )
    fig.update_layout(xaxis_title="Día", yaxis_title="Costo ($)", height=350)
    fig.update_traces(line_color="darkred")
    return fig


def chart_demanda_vs_dia(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(df, x="dia", y="demanda_cc", title="Demanda diaria de Heparina")
    fig.update_layout(xaxis_title="Día", yaxis_title="Demanda (cc)", height=350)
    fig.update_traces(marker_color="#2ca02c")
    return fig


def chart_replicas_ctf(df: pd.DataFrame) -> go.Figure:
    replicas = df[df["replica"].apply(lambda x: isinstance(x, int))].copy()
    fig = px.bar(replicas, x="replica", y="CTF", title="CTF por réplica")
    fig.update_layout(xaxis_title="Réplica", yaxis_title="CTF ($)", height=350)
    fig.update_traces(marker_color="coral")
    return fig


def chart_optimizacion_ctf(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    df_plot = df.nsmallest(top_n, "CTF_promedio").copy()
    df_plot["combinacion"] = (
        df_plot["punto_emision_pedido"].astype(str)
        + " / "
        + df_plot["tamaño_pedido"].astype(str)
    )
    fig = px.bar(
        df_plot,
        x="CTF_promedio",
        y="combinacion",
        orientation="h",
        title=f"Top {top_n} combinaciones por CTF promedio (menor a mayor)",
    )
    fig.update_layout(
        xaxis_title="CTF promedio ($)",
        yaxis_title="PEP / TP",
        height=400,
        yaxis={"categoryorder": "total descending"},
    )
    fig.update_traces(marker_color="teal", texttemplate="%{x:,.0f}", textposition="outside")
    return fig


def chart_optimizacion_mejor_detalle(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df, x="dia", y="stock_final", title="Mejor combinación: evolución del stock"
    )
    fig.update_layout(xaxis_title="Día", yaxis_title="Stock (cc)", height=350)
    fig.update_traces(line_color="steelblue")
    return fig