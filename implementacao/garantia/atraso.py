"""Cálculo do Atraso (RF01): minutos entre o Prazo Prometido e a Confirmação de Entrega."""
import math
from datetime import datetime


def calcular_atraso_min(prazo_prometido: datetime, confirmada_em: datetime) -> int:
    segundos = (confirmada_em - prazo_prometido).total_seconds()
    if segundos <= 0:
        return 0
    # Qualquer fração de minuto conta como minuto inteiro: 2h00m01s é "acima de 2 h".
    return math.ceil(segundos / 60)
