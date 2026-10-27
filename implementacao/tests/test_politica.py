"""Casos do plano de testes (docs/03-testes.md) para a Política de Compensação."""
import unittest
from decimal import Decimal

from garantia.politica import Varejo


class VarejoTest(unittest.TestCase):
    def setUp(self):
        self.politica = Varejo()

    def test_ct01_atraso_de_2h00_nao_gera_credito(self):
        self.assertEqual(self.politica.calcular_credito(120, Decimal("300.00")), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
