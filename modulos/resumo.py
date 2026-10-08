# -*- coding: utf-8 -*-
"""
modulos/resumo.py
=================
O RESUMO DA VIAGEM. Ao encerrar (comando "encerrar viagem") consolida tudo:
distância total, paradas, locais, emoção predominante, maior trecho sem parar
e as fotos em ordem cronológica. Parte obrigatória da demonstração.
"""
from collections import Counter


def gerar(diario, localizacao):
    regs = diario.registros
    if not regs:
        print("\nNenhum registro na viagem.")
        return

    distancia = localizacao.distancia_total_km
    paradas = localizacao.paradas_feitas
    locais = len(regs)

    emocoes = [r["estado_voz"] for r in regs]
    emocao_predominante = Counter(emocoes).most_common(1)[0][0]

    maior_trecho = max(r["contexto"]["tempo_desde_ultima_parada_min"] for r in regs)

    print("\n" + "=" * 64)
    print("RESUMO DA VIAGEM")
    print("=" * 64)
    print(f"  Distância total.............: {distancia} km")
    print(f"  Paradas realizadas..........: {paradas}")
    print(f"  Locais registrados..........: {locais}")
    print(f"  Emoção predominante.........: {emocao_predominante.capitalize()}")
    print(f"  Maior trecho sem parar......: {maior_trecho} min")
    print("\n  Fotos em ordem cronológica:")
    for r in regs:
        print(f"   {r['numero']:02d}. {r['foto']:22s} "
              f"{r['local']:22s} → {r['decisao_random_forest']}")
    print("=" * 64)

    return {
        "distancia_total_km": distancia,
        "paradas": paradas,
        "locais_registrados": locais,
        "emocao_predominante": emocao_predominante,
        "maior_trecho_sem_parada_min": maior_trecho,
    }
