"""Tests para los generadores de variables aleatorias (transformada inversa)."""

import math

import pytest

from simulacion_clinica.generadores import (
    demanda_LMV,
    demanda_MJS,
    demora_proveedor,
)


class TestDemandaLMV:
    """Generador de la demanda diaria Lun/Mié/Vie: x = 74 + 18*r."""

    def test_dentro_del_rango(self):
        for r in (0.0, 0.1, 0.5, 0.9, 1.0):
            valor = demanda_LMV(r)
            assert 74 <= valor <= 92

    def test_limite_inferior(self):
        assert demanda_LMV(0.0) == 74

    def test_limite_superior(self):
        assert demanda_LMV(1.0) == 92

    def test_formula_exacta(self):
        assert demanda_LMV(0.5) == pytest.approx(74 + 18 * 0.5)


class TestDemandaMJS:
    """Generador de la demanda diaria Mar/Jue/Sáb: x = 62 + 14*r."""

    def test_dentro_del_rango(self):
        for r in (0.0, 0.3, 0.7, 1.0):
            valor = demanda_MJS(r)
            assert 62 <= valor <= 76

    def test_limite_inferior(self):
        assert demanda_MJS(0.0) == 62

    def test_limite_superior(self):
        assert demanda_MJS(1.0) == 76

    def test_formula_exacta(self):
        assert demanda_MJS(0.5) == pytest.approx(62 + 14 * 0.5)


class TestDemoraProveedor:
    """Generador de la demora del proveedor: x = 10 - 2.58*ln(r)."""

    def test_mayor_o_igual_a_10(self):
        for r in (0.01, 0.1, 0.5, 0.9, 0.99):
            valor = demora_proveedor(r)
            assert valor >= 10

    def test_formula_exacta(self):
        r = 0.5
        esperado = 10 - 2.58 * math.log(r)
        assert demora_proveedor(r) == pytest.approx(esperado)

    def test_r_cercano_a_cero_no_falla(self):
        # r muy chico => ln(r) muy negativo => valor grande pero finito
        valor = demora_proveedor(1e-10)
        assert math.isfinite(valor)
        assert valor >= 10

    def test_r_cercano_a_uno_tiende_al_minimo(self):
        # r -> 1 => ln(r) -> 0 => valor -> 10
        valor = demora_proveedor(0.999999)
        assert pytest.approx(valor, abs=1e-3) == 10
