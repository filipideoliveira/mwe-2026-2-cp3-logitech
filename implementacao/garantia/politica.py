"""Política de Compensação da Garantia de Prazo (RF02, RF03 e RF04)."""
from decimal import ROUND_HALF_UP, Decimal

CENTAVO = Decimal("0.01")

# Limite superior inclusivo de cada faixa, em minutos, e o percentual do frete.
FAIXAS = (
    (120, Decimal("0")),
    (1440, Decimal("0.10")),
    (4320, Decimal("0.25")),
)
PERCENTUAL_ACIMA_DE_72H = Decimal("0.50")


def percentual_da_faixa(atraso_min: int) -> Decimal:
    for limite_min, percentual in FAIXAS:
        if atraso_min <= limite_min:
            return percentual
    return PERCENTUAL_ACIMA_DE_72H


class Varejo:
    TETO = Decimal("500.00")

    def calcular_credito(self, atraso_min: int, frete: Decimal) -> Decimal:
        credito = (frete * percentual_da_faixa(atraso_min)).quantize(CENTAVO, ROUND_HALF_UP)
        return min(credito, self.TETO)


class Corporativo:
    TETO = Decimal("2000.00")

    def calcular_credito(self, atraso_min: int, frete: Decimal) -> Decimal:
        credito = (frete * percentual_da_faixa(atraso_min) * 2).quantize(CENTAVO, ROUND_HALF_UP)
        return min(credito, self.TETO)
