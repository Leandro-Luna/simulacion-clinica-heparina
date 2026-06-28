"""Punto de entrada del modelo de optimización por punto de emisión.

Prueba una grilla de combinaciones (PEP × tamaño de pedido) para encontrar
la que minimiza el CTF promedio. Exporta los resultados a Excel.
"""

import pandas as pd

from simulacion_clinica.optimizacion import (
    ConfigOptimizacion,
    optimizar,
    simular_optimizacion,
)

ARCHIVO_SALIDA = "resultado_optimizacion.xlsx"

PUNTOS_EMISION = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
TAMANIOS_PEDIDO = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]


def main() -> None:
    cfg = ConfigOptimizacion()

    print("=" * 80)
    print("OPTIMIZACIÓN: PUNTO DE EMISIÓN DE PEDIDO (PEP) × TAMAÑO DE PEDIDO")
    print("=" * 80)
    print(f"Período: {cfg.fecha_inicio} + {cfg.TF} días")
    print(f"Réplicas por combinación: {cfg.n_replicas}")
    print(f"Nivel de confianza: {1 - cfg.alpha:.0%} (alpha={cfg.alpha})")
    print(f"Puntos de emisión: {PUNTOS_EMISION}")
    print(f"Tamaños de pedido: {TAMANIOS_PEDIDO}")
    print(f"Total de combinaciones: {len(PUNTOS_EMISION) * len(TAMANIOS_PEDIDO)}")
    print()

    df_resultados = optimizar(cfg, PUNTOS_EMISION, TAMANIOS_PEDIDO)

    # Sin límites de display
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

    print("-" * 80)
    print("RESUMEN DE COMBINACIONES (ordenadas por CTF promedio ascendente)")
    print("-" * 80)
    print(df_resultados.to_string(index=False))
    print()

    # Mejor combinación
    mejor = df_resultados.iloc[0]
    print("-" * 80)
    print("MEJOR COMBINACIÓN")
    print("-" * 80)
    print(f"  Punto de emisión (PEP): {int(mejor['punto_emision_pedido'])} cc")
    print(f"  Tamaño de pedido:       {int(mejor['tamaño_pedido'])} cc")
    print(f"  CTF promedio:           ${mejor['CTF_promedio']:,.2f}")
    print(f"  IC ({1 - cfg.alpha:.0%}): [{mejor['IC_inf']:,.2f}, {mejor['IC_sup']:,.2f}]")
    print(f"  Emergencias promedio:   {mejor['n_emergencias_prom']:.2f}")
    print(f"  Pedidos promedio:       {mejor['n_pedidos_prom']:.2f}")
    print()

    # Correr la mejor combinación para obtener el detalle por día
    cfg_mejor = ConfigOptimizacion(
        fecha_inicio=cfg.fecha_inicio,
        TF=cfg.TF,
        n_replicas=cfg.n_replicas,
        ST_inicial=cfg.ST_inicial,
        cantidad_emergencia=cfg.cantidad_emergencia,
        SS=cfg.SS,
        TP=int(mejor["tamaño_pedido"]),
        punto_emision_pedido=int(mejor["punto_emision_pedido"]),
        costo_unitario_pedido=cfg.costo_unitario_pedido,
        costo_unitario_emergencia=cfg.costo_unitario_emergencia,
        seed=None,
        alpha=cfg.alpha,
    )
    df_mejor, _ = simular_optimizacion(cfg_mejor)

    # Exportar a Excel
    with pd.ExcelWriter(ARCHIVO_SALIDA, engine="openpyxl") as writer:
        df_resultados.to_excel(writer, sheet_name="Resumen Combinaciones", index=False)
        df_mejor.to_excel(writer, sheet_name="Mejor Combinación", index=False)

    print(f"Resultados exportados a: {ARCHIVO_SALIDA}")


if __name__ == "__main__":
    main()
