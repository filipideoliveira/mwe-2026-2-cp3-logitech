"""Validação de ausência do destinatário (RF05): Strategy isolada do cálculo do crédito."""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta

RAIO_TERRA_M = 6_371_000
RAIO_GEOCERCA_M = 200
JANELA_PARADA = timedelta(minutes=10)


@dataclass(frozen=True)
class Posicao:
    instante: datetime
    lat: float
    lon: float


def distancia_m(origem: tuple, destino: tuple) -> float:
    """Distância de haversine, arredondada ao centímetro para não errar o limite de 200 m."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*origem, *destino))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return round(2 * RAIO_TERRA_M * math.asin(math.sqrt(a)), 2)


class ValidacaoAusencia:
    def comprovada(self, endereco: tuple, registrada_em: datetime, posicoes: list) -> bool:
        anteriores = sorted((p for p in posicoes if p.instante <= registrada_em), key=lambda p: p.instante)

        # Parada = posições seguidas dentro da geocerca até o registro. Um pacote perdido não
        # interrompe a parada (RNF01); uma posição fora da geocerca, sim.
        inicio_parada = None
        for posicao in reversed(anteriores):
            if distancia_m(endereco, (posicao.lat, posicao.lon)) > RAIO_GEOCERCA_M:
                break
            inicio_parada = posicao.instante

        return inicio_parada is not None and inicio_parada <= registrada_em - JANELA_PARADA
