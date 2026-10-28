"""Casos do plano de testes para o cálculo do atraso (RF01)."""
import unittest
from datetime import datetime

from garantia.atraso import calcular_atraso_min

PRAZO = datetime(2026, 10, 27, 10, 0, 0)


class AtrasoTest(unittest.TestCase):
    def test_ct15_entrega_antes_do_prazo_tem_atraso_zero(self):
        self.assertEqual(calcular_atraso_min(PRAZO, datetime(2026, 10, 27, 9, 0, 0)), 0)

    def test_entrega_exatamente_2h00m00s_depois_tem_120_min(self):
        self.assertEqual(calcular_atraso_min(PRAZO, datetime(2026, 10, 27, 12, 0, 0)), 120)

    def test_ct32_fracao_de_minuto_arredonda_para_cima(self):
        self.assertEqual(calcular_atraso_min(PRAZO, datetime(2026, 10, 27, 12, 0, 1)), 121)


if __name__ == "__main__":
    unittest.main()
