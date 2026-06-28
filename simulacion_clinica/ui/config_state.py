"""Estado compartido de configuración entre vistas de la UI."""

from dataclasses import dataclass, fields
from datetime import date

from simulacion_clinica.config import Config
from simulacion_clinica.optimizacion import ConfigOptimizacion


@dataclass
class UIConfigState:
    """Parámetros editables desde la UI.

    Combina campos comunes de Config y ConfigOptimizacion, más los rangos
    de optimización.
    """

    # Tiempo
    fecha_inicio: date = date(2026, 1, 1)
    TF: int = 365
    n_replicas: int = 100

    # Stock
    ST_inicial: int = 1000
    PE: int = 500  # cantidad de emergencia (nombre compartido)
    SS: int = 300
    TP: int = 1500

    # Costos
    costo_unitario_pedido: int = 1150
    costo_unitario_emergencia: int = 2300

    # Ventana de pedido programado (solo modelo base)
    dia_pedido_desde: int = 15
    dia_pedido_hasta: int = 20

    # Optimización (PEP)
    punto_emision_pedido: int = 2000
    pep_min: int = 500
    pep_max: int = 4000
    pep_paso: int = 500
    tp_min: int = 500
    tp_max: int = 4000
    tp_paso: int = 500

    # Aleatoriedad
    seed: int | None = None
    alpha: float = 0.05

    @classmethod
    def from_defaults(cls) -> "UIConfigState":
        return cls()

    def to_config(self) -> Config:
        return Config(
            fecha_inicio=self.fecha_inicio,
            TF=self.TF,
            n_replicas=self.n_replicas,
            ST_inicial=self.ST_inicial,
            PE=self.PE,
            SS=self.SS,
            TP=self.TP,
            costo_unitario_pedido=self.costo_unitario_pedido,
            costo_unitario_emergencia=self.costo_unitario_emergencia,
            dia_pedido_desde=self.dia_pedido_desde,
            dia_pedido_hasta=self.dia_pedido_hasta,
            seed=self.seed,
            alpha=self.alpha,
        )

    def to_config_optimizacion(self) -> ConfigOptimizacion:
        return ConfigOptimizacion(
            fecha_inicio=self.fecha_inicio,
            TF=self.TF,
            n_replicas=self.n_replicas,
            ST_inicial=self.ST_inicial,
            cantidad_emergencia=self.PE,
            SS=self.SS,
            TP=self.TP,
            punto_emision_pedido=self.punto_emision_pedido,
            costo_unitario_pedido=self.costo_unitario_pedido,
            costo_unitario_emergencia=self.costo_unitario_emergencia,
            seed=self.seed,
            alpha=self.alpha,
        )

    def reset(self) -> None:
        defaults = self.from_defaults()
        for field in fields(self):
            setattr(self, field.name, getattr(defaults, field.name))