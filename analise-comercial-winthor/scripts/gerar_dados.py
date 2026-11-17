"""Gera dados fictícios e reproduzíveis para demonstrar as análises."""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

ENTRADA = Path(__file__).resolve().parents[1] / "dados" / "entrada"
ENTRADA.mkdir(parents=True, exist_ok=True)
RNG = random.Random(658)


def salvar_csv(nome, cabecalho, linhas):
    caminho = ENTRADA / nome
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)


def gerar_dados():
    cidades = ["São Paulo", "Guarulhos", "Osasco", "Santo André", "Jundiaí"]
    clientes = [
        (12000 + numero, f"Cliente exemplo {numero:03d}", RNG.choice(cidades))
        for numero in range(1, 81)
    ]
    produtos = [
        (20690, "20690", "Pão de queijo tradicional", 658, 12),
        (20691, "20691", "Pão de queijo coquetel", 658, 10),
        (20692, "20692", "Waffle congelado", 658, 8),
        (30185, "30185", "Batata congelada", 7, 6),
        (30186, "30186", "Vegetais congelados", 7, 10),
    ]

    notas = []
    movimentos = []
    transacao = 100000
    movimento_id = 1

    for deslocamento in range(150):
        dia = date(2026, 7, 1) + timedelta(days=deslocamento)
        if dia > date(2026, 11, 17):
            break

        for _ in range(RNG.randint(1, 8)):
            cliente = RNG.choice(clientes)[0]
            produto = RNG.choice(produtos)
            transacao += 1
            condicao = 5 if RNG.random() < 0.08 else 1
            cancelamento = dia.isoformat() if RNG.random() < 0.025 else ""

            notas.append(
                (transacao, cliente, 1, dia.isoformat(), condicao, cancelamento)
            )
            movimentos.append(
                (
                    movimento_id,
                    transacao,
                    produto[0],
                    "S",
                    RNG.randint(1, 30),
                    round(RNG.uniform(8, 45), 2),
                )
            )
            movimento_id += 1

    salvar_csv("clientes.csv", ["codcli", "cliente", "cidade"], clientes)
    salvar_csv(
        "produtos.csv",
        ["codprod", "codfab", "descricao", "codfornec", "unidades_por_caixa"],
        produtos,
    )
    salvar_csv(
        "notas.csv",
        ["numtransvenda", "codcli", "codfilial", "dtsaida", "condvenda", "dtcancel"],
        notas,
    )
    salvar_csv(
        "movimentos.csv",
        ["id", "numtransvenda", "codprod", "codoper", "qt", "punit"],
        movimentos,
    )
    print(f"Dados fictícios gerados: {len(clientes)} clientes e {len(notas)} notas.")


if __name__ == "__main__":
    gerar_dados()
