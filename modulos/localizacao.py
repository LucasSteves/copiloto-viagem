# -*- coding: utf-8 -*-
"""
modulos/localizacao.py
======================
Registra ONDE e QUANDO cada evento aconteceu, e mantém o contexto da viagem
(tempo total, distância, paradas) — que alimenta tanto o diário quanto o
Random Forest.

Como o notebook não tem GPS, usamos uma LISTA DE CIDADES simulada (o enunciado
permite começar assim). Cada ativação "anda" um trecho na rota.
"""
from datetime import datetime

# Rota simulada: nome legível + coordenadas aproximadas + km desde a anterior.
ROTA = [
    ("Indaiatuba - SP",       (-23.09, -47.21),  0),
    ("Itu - SP",              (-23.26, -47.30), 25),
    ("Salto - SP",            (-23.20, -47.29), 12),
    ("Serra Negra - SP",      (-22.61, -46.70), 95),
    ("Águas de Lindóia - SP", (-22.47, -46.63), 22),
    ("Monte Verde - MG",      (-22.86, -46.03), 88),
    ("Campos do Jordão - SP", (-22.73, -45.59), 75),
]


class Localizacao:
    """Guarda o estado da viagem e avança na rota a cada registro."""

    def __init__(self):
        self.indice = 0
        self.inicio = datetime.now()
        self.distancia_total_km = 0
        self.paradas_feitas = 0
        self.ultimo_tempo_parada = datetime.now()

    def registrar(self):
        """Avança um trecho e devolve os dados de local + contexto."""
        nome, coords, km = ROTA[self.indice % len(ROTA)]
        self.distancia_total_km += km
        self.indice += 1

        agora = datetime.now()
        tempo_desde_parada = int((agora - self.ultimo_tempo_parada).total_seconds() / 60)

        return {
            "nome_local": nome,
            "coordenadas": coords,
            "horario": agora.strftime("%d/%m/%Y - %H:%M"),
            "hora_do_dia": agora.hour,
            "distancia_total_km": self.distancia_total_km,
            "paradas_feitas": self.paradas_feitas,
            "tempo_desde_ultima_parada_min": tempo_desde_parada,
        }

    def marcar_parada(self):
        """Chamado quando a decisão foi de parar/abastecer/comer: zera o
        cronômetro de tempo sem parar e soma uma parada."""
        self.paradas_feitas += 1
        self.ultimo_tempo_parada = datetime.now()


# --- MODO DEMONSTRAÇÃO -----------------------------------------------------
# Para a apresentação vale forçar um cenário convincente (ex.: 2h40 dirigindo,
# voz cansada, posto na frente). Use simular_contexto() para injetar valores.
def simular_contexto(loc, tempo_min=None, distancia=None, hora=None):
    dados = loc.registrar()
    if tempo_min is not None:
        dados["tempo_desde_ultima_parada_min"] = tempo_min
    if distancia is not None:
        dados["distancia_total_km"] = distancia
    if hora is not None:
        dados["hora_do_dia"] = hora
    return dados
