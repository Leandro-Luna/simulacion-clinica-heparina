"""Generadores de variables aleatorias vía Método de la Transformada Inversa.

Las fórmulas y sus parámetros están definidos por el enunciado del TP:

  - Demanda diaria Lun/Mié/Vie:  x = 74 + 18*r   (Uniforme 74-92)
  - Demanda diaria Mar/Jue/Sáb:  x = 62 + 14*r   (Uniforme 62-76)
  - Demora del proveedor:        x = 10 - 2.58*ln(r)  (Exponencial desplazada)

Cada función recibe un número pseudoaleatorio r en (0, 1] y devuelve el valor
generado por la transformada inversa.
"""

import math


def demanda_LMV(r: float) -> float:
    """Demanda diaria de Heparina para Lunes/Miércoles/Viernes.

    Fórmula (transformada inversa): x = 74 + 18*r  =>  Uniforme(74, 92)
    """
    return 74 + 18 * r


def demanda_MJS(r: float) -> float:
    """Demanda diaria de Heparina para Martes/Jueves/Sábados.

    Fórmula (transformada inversa): x = 62 + 14*r  =>  Uniforme(62, 76)
    """
    return 62 + 14 * r


def demora_proveedor(r: float) -> float:
    """Demora de entrega del proveedor en días.

    Fórmula (transformada inversa): x = 10 - 2.58*ln(r)
    El mínimo estructural es 10 días; la variabilidad se suma por encima.
    """
    return 10 - 2.58 * math.log(r)
