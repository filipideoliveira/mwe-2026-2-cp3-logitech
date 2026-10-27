"""Política de Compensação da Garantia de Prazo (RF02, RF03 e RF04)."""
from decimal import Decimal


class Varejo:
    def calcular_credito(self, atraso_min: int, frete: Decimal) -> Decimal:
        return Decimal("0.00")
