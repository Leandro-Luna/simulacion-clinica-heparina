"""Utilidades de exportación para la UI."""

import pandas as pd


def exportar_simulacion(
    df_corrida1: pd.DataFrame,
    df_resumen: pd.DataFrame,
    ruta: str = "resultado_simulacion.xlsx",
) -> str:
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df_corrida1.to_excel(writer, sheet_name="Corrida 1", index=False)
        df_resumen.to_excel(writer, sheet_name="Resumen Réplicas", index=False)
    return ruta


def exportar_optimizacion(
    df_resultados: pd.DataFrame,
    df_mejor: pd.DataFrame,
    ruta: str = "resultado_optimizacion.xlsx",
) -> str:
    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df_resultados.to_excel(writer, sheet_name="Resumen Combinaciones", index=False)
        df_mejor.to_excel(writer, sheet_name="Mejor Combinación", index=False)
    return ruta


def exportar_simulacion_bytes(df_corrida1: pd.DataFrame, df_resumen: pd.DataFrame) -> bytes:
    """Genera el Excel en memoria y retorna los bytes para st.download_button."""
    import io

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_corrida1.to_excel(writer, sheet_name="Corrida 1", index=False)
        df_resumen.to_excel(writer, sheet_name="Resumen Réplicas", index=False)
    buffer.seek(0)
    return buffer.getvalue()


def exportar_optimizacion_bytes(
    df_resultados: pd.DataFrame, df_mejor: pd.DataFrame
) -> bytes:
    """Genera el Excel en memoria y retorna los bytes para st.download_button."""
    import io

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_resultados.to_excel(writer, sheet_name="Resumen Combinaciones", index=False)
        df_mejor.to_excel(writer, sheet_name="Mejor Combinación", index=False)
    buffer.seek(0)
    return buffer.getvalue()