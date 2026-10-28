"""Casos do plano de testes para a validação de ausência (RF05)."""
import math
import unittest
from datetime import datetime, timedelta

from garantia.ausencia import Posicao, ValidacaoAusencia, RAIO_TERRA_M

ENDERECO = (-23.5740, -46.6230)
REGISTRO = datetime(2026, 10, 27, 14, 0, 0)


def ao_norte(metros: float, instante: datetime) -> Posicao:
    lat, lon = ENDERECO
    return Posicao(instante, lat + math.degrees(metros / RAIO_TERRA_M), lon)


def parado(metros: float, inicio: datetime, fim: datetime, sem=()) -> list:
    posicoes, instante = [], inicio
    while instante <= fim:
        if instante not in sem:
            posicoes.append(ao_norte(metros, instante))
        instante += timedelta(seconds=30)
    return posicoes


class ValidacaoAusenciaTest(unittest.TestCase):
    def setUp(self):
        self.validacao = ValidacaoAusencia()

    def comprovada(self, posicoes) -> bool:
        return self.validacao.comprovada(ENDERECO, REGISTRO, posicoes)

    def test_ct19_parado_a_200m_por_10min00_comprova_ausencia(self):
        self.assertTrue(self.comprovada(parado(200, datetime(2026, 10, 27, 13, 50, 0), REGISTRO)))

    def test_ct20_parado_a_201m_nao_comprova_ausencia(self):
        self.assertFalse(self.comprovada(parado(201, datetime(2026, 10, 27, 13, 50, 0), REGISTRO)))

    def test_ct21_parado_por_9min59_nao_comprova_ausencia(self):
        posicoes = parado(150, datetime(2026, 10, 27, 13, 50, 1), REGISTRO)
        posicoes.append(ao_norte(150, REGISTRO))
        self.assertFalse(self.comprovada(posicoes))

    def test_chegada_de_longe_conta_a_parada_so_a_partir_da_geocerca(self):
        longe = parado(5000, datetime(2026, 10, 27, 13, 40, 0), datetime(2026, 10, 27, 13, 49, 30))
        perto = parado(100, datetime(2026, 10, 27, 13, 50, 0), REGISTRO)
        self.assertTrue(self.comprovada(longe + perto))

    def test_pacote_perdido_na_janela_nao_invalida_a_parada(self):
        # RNF01: a telemetria tolera perda; a ausência de um pacote não quebra a parada.
        perdido = datetime(2026, 10, 27, 13, 55, 0)
        posicoes = parado(100, datetime(2026, 10, 27, 13, 50, 0), REGISTRO, sem=(perdido,))
        self.assertTrue(self.comprovada(posicoes))

    def test_sem_posicoes_nao_comprova_ausencia(self):
        self.assertFalse(self.comprovada([]))


if __name__ == "__main__":
    unittest.main()
