"""Punto de entrada de la simulación de gestión de stock de Heparina.

Ejecuta N réplicas de la simulación, muestra en consola el detalle de la
primera corrida y el resumen de todas las réplicas, y exporta los resultados
a un archivo Excel con dos hojas.
"""

import pandas as pd

from simulacion_clinica.config import Config
from simulacion_clinica.simulacion import simular_replicas

ARCHIVO_SALIDA = "resultado_simulacion.xlsx"


def main() -> None:
    cfg = Config()  # seed=None => aleatoria por corrida

    print("=" * 80)
    print("SIMULACIÓN DE GESTIÓN DE STOCK DE HEPARINA - CENTRO DE DIÁLISIS")
    print("=" * 80)
    print(f"Período: {cfg.fecha_inicio} + {cfg.TF} días")
    print(f"Réplicas: {cfg.n_replicas}")
    print()

    df_corrida1, df_resumen = simular_replicas(cfg)

    # Sin límites de display
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

    print("-" * 80)
    print("CORRIDA 1 - DETALLE POR DÍA")
    print("-" * 80)
    print(df_corrida1.to_string(index=False))
    print()

    print("-" * 80)
    print(f"RESUMEN DE {cfg.n_replicas} RÉPLICAS")
    print("-" * 80)
    print(df_resumen.to_string(index=False))
    print()

    # Exportar a Excel con dos hojas
    with pd.ExcelWriter(ARCHIVO_SALIDA, engine="openpyxl") as writer:
        df_corrida1.to_excel(writer, sheet_name="Corrida 1", index=False)
        df_resumen.to_excel(writer, sheet_name="Resumen Réplicas", index=False)

    print(f"Resultados exportados a: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
