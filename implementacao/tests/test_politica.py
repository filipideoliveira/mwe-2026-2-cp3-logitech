"""Casos do plano de testes (docs/03-testes.md) para a Política de Compensação."""
import unittest
from decimal import Decimal

from garantia.politica import Varejo


class VarejoTest(unittest.TestCase):
    def setUp(self):
        self.politica = Varejo()

    def test_ct01_atraso_de_2h00_nao_gera_credito(self):
        self.assertEqual(self.politica.calcular_credito(120, Decimal("300.00")), Decimal("0.00"))

    def test_ct02_atraso_de_2h01_gera_10_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(121, Decimal("300.00")), Decimal("30.00"))

    def test_ct03_atraso_de_24h00_ainda_gera_10_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(1440, Decimal("300.00")), Decimal("30.00"))

    def test_ct04_atraso_de_24h01_gera_25_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(1441, Decimal("300.00")), Decimal("75.00"))

    def test_ct05_atraso_de_72h00_ainda_gera_25_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(4320, Decimal("300.00")), Decimal("75.00"))

    def test_ct06_atraso_de_72h01_gera_50_por_cento(self):
        self.assertEqual(self.politica.calcular_credito(4321, Decimal("300.00")), Decimal("150.00"))


if __name__ == "__main__":
    unittest.main()
