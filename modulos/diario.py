# -*- coding: utf-8 -*-
"""
modulos/diario.py
=================
O DIÁRIO DE BORDO. Cada comando bem-sucedido vira uma entrada completa,
salva em JSON (para o resumo depois) e impressa no formato do enunciado.
"""
import json
import os

import config as cfg


class Diario:
    def __init__(self):
        self.registros = []
        # começa do zero a cada viagem
        if os.path.exists(cfg.CAMINHO_DIARIO):
            os.remove(cfg.CAMINHO_DIARIO)

    def adicionar(self, contexto, comando, emocao, conf_emocao,
                  classe_img, conf_img, decisao, conf_decisao,
                  justificativa, foto):
        n = len(self.registros) + 1
        reg = {
            "numero": n,
            "horario": contexto["horario"],
            "local": contexto["nome_local"],
            "coordenadas": contexto["coordenadas"],
            "comando": comando,
            "estado_voz": emocao,
            "confianca_voz": conf_emocao,
            "imagem_classificada": classe_img,
            "confianca_imagem": conf_img,
            "decisao_random_forest": decisao,
            "confianca_decisao": conf_decisao,
            "justificativa": justificativa,
            "foto": os.path.basename(foto) if foto else "(simulada)",
            # contexto bruto — útil para explicar a decisão na banca
            "contexto": {
                "tempo_desde_ultima_parada_min": contexto["tempo_desde_ultima_parada_min"],
                "distancia_total_km": contexto["distancia_total_km"],
                "paradas_feitas": contexto["paradas_feitas"],
                "hora_do_dia": contexto["hora_do_dia"],
            },
        }
        self.registros.append(reg)
        self._salvar()
        self._imprimir(reg)
        return reg

    def _salvar(self):
        os.makedirs(os.path.dirname(cfg.CAMINHO_DIARIO), exist_ok=True)
        with open(cfg.CAMINHO_DIARIO, "w", encoding="utf-8") as f:
            json.dump(self.registros, f, ensure_ascii=False, indent=2)

    def _imprimir(self, r):
        print("\n" + "─" * 64)
        print(f"DIÁRIO DE BORDO  ·  Registro {r['numero']:02d}")
        print("─" * 64)
        print(f"Horário: {r['horario']}     Local: {r['local']}")
        print(f"Coordenadas: {r['coordenadas'][0]}, {r['coordenadas'][1]}")
        print(f"Comando reconhecido:  \"{r['comando']}\"")
        print(f"Estado da voz:  {r['estado_voz'].upper()} — {r['confianca_voz']}%")
        print(f"Imagem classificada:  {r['imagem_classificada']} — {r['confianca_imagem']}%")
        print(f"Decisão do Random Forest:  {r['decisao_random_forest']} — {r['confianca_decisao']}%")
        print(f"  ↳ {r['justificativa']}")
        print(f"Foto associada:  {r['foto']}")
