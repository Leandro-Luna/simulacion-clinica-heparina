"""Componente reutilizable para mostrar DataFrames de pandas en Flet."""

import flet as ft
import pandas as pd

MAX_ROWS_DEFAULT = 200


def dataframe_to_datatable(
    df: pd.DataFrame,
    max_rows: int = MAX_ROWS_DEFAULT,
    wrap: bool = False,
) -> ft.DataTable:
    """Convierte un DataFrame en un ft.DataTable paginado.

    Args:
        df: DataFrame a mostrar.
        max_rows: Cantidad máxima de filas a renderizar.
        wrap: Si es True, permite que las celdas ocupen varias líneas.
    """
    df = df.head(max_rows)

    columns = [
        ft.DataColumn(
            ft.Text(str(col), weight=ft.FontWeight.BOLD),
            numeric=pd.api.types.is_numeric_dtype(df[col]),
        )
        for col in df.columns
    ]

    rows: list[ft.DataRow] = []
    for _, record in df.iterrows():
        cells = []
        for col in df.columns:
            value = record[col]
            if isinstance(value, float):
                text = f"{value:,.2f}"
            elif isinstance(value, int):
                text = f"{value:,}"
            else:
                text = str(value)
            cells.append(
                ft.DataCell(
                    ft.Text(text, no_wrap=not wrap),
                )
            )
        rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.border_radius.all(8),
        vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        data_row_min_height=40,
    )
