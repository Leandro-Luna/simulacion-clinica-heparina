"""Configuración de parámetros para la simulación de gestión de stock de Heparina."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Config:
    """Parámetros configurables de la simulación.

    Todos los valores por defecto provienen del enunciado del TP y del flowchart.
    """

    # --- Tiempo ---
    fecha_inicio: date = date(2026, 1, 1)
    TF: int = 365  # días a simular (1 año)
    delta_t: int = 1
    n_replicas: int = 100  # cantidad de réplicas de la simulación

    # --- Stock (en cc) ---
    ST_inicial: int = 1000  # stock inicial
    PE: int = 500  # tamaño compra de emergencia (cc)
    SS: int = 300  # stock de seguridad (umbral de emergencia)
    TP: int = 1500  # tamaño del pedido programado (cc)

    # --- Costos ---
    costo_unitario_pedido: int = 1150  # costo por cc de pedido programado
    costo_unitario_emergencia: int = 2300  # costo por cc de compra de emergencia

    # --- Ventana de pedido programado ---
    dia_pedido_desde: int = 15
    dia_pedido_hasta: int = 20

    # --- Aleatoriedad ---
    seed: int | None = None  # None => aleatoria por corrida

    # --- Intervalo de confianza ---
    alpha: float = 0.05  # nivel de significancia (0.05 = 95% de confianza)
