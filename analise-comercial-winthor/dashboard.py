"""Painel local e demonstrativo de vendas, clientes e produtos."""

from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
import csv
import json
import sqlite3

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
ENTRADA = ROOT / "dados" / "entrada"


st.set_page_config(
    page_title="Análise comercial | Distribuição", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.035em;
    }

    /* Fundo dos indicadores */
    [data-testid="stMetric"] {
        background-color: #1E293B;
        padding: 20px 24px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    /* Títulos dos indicadores */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {
        color: #CBD5E1 !important;
        font-size: 14px;
        font-weight: 500;
    }

    /* Valores dos indicadores */
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #FFFFFF !important;
        font-size: 30px;
        font-weight: 700;
    }

    /* Variações positivas */
    [data-testid="stMetricDelta"] {
        color: #22C55E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def carregar_base():
    """Banco descartável; não altera os arquivos nem exige acesso ao WinThor."""
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(
            (ROOT / "sql" / "01_estrutura.sql").read_text(encoding="utf-8")
        )
        for tabela in ("clientes", "produtos", "notas", "movimentos"):
            with (ENTRADA / f"{tabela}.csv").open(
                encoding="utf-8-sig", newline=""
            ) as arquivo:
                leitor = csv.DictReader(arquivo)
                colunas = leitor.fieldnames
                linhas = list(leitor)
            if not colunas:
                raise ValueError(f"Arquivo vazio ou sem cabeçalho: {tabela}.csv")
            if linhas:
                marcadores = ",".join("?" for _ in colunas)
                con.executemany(
                    f'INSERT INTO {tabela} ({",".join(colunas)}) VALUES ({marcadores})',
                    [[linha[col] or None for col in colunas] for linha in linhas],
                )
        vendas = pd.read_sql_query(
            """
            SELECT n.numtransvenda, n.codcli, c.cliente, c.cidade, n.codfilial,
                   n.dtsaida, n.condvenda, n.dtcancel, m.codprod, p.codfab,
                   p.descricao, p.codfornec, p.unidades_por_caixa, m.codoper,
                   m.qt, m.punit, ROUND(m.qt*m.punit,2) AS valor
            FROM notas n
            JOIN clientes c ON c.codcli=n.codcli
            JOIN movimentos m ON m.numtransvenda=n.numtransvenda
            JOIN produtos p ON p.codprod=m.codprod
        """,
            con,
        )
        clientes = pd.read_sql_query(
            "SELECT codcli, cliente, cidade FROM clientes", con
        )
        produtos = pd.read_sql_query("SELECT * FROM produtos", con)
    finally:
        con.close()
    vendas["dtsaida"] = pd.to_datetime(vendas["dtsaida"]).dt.date
    return vendas, clientes, produtos


def csv_bytes(df):
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")


def excel_bytes(tabelas):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    wb.remove(wb.active)
    for nome, df in tabelas.items():
        ws = wb.create_sheet(nome[:31])
        ws.append(list(df.columns))
        for row in df.itertuples(index=False, name=None):
            ws.append(
                [
                    (
                        v.isoformat()
                        if isinstance(v, date)
                        else (v.item() if hasattr(v, "item") else v)
                    )
                    for v in row
                ]
            )
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="17365D")
            cell.font = Font(bold=True, color="FFFFFF")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for idx, coluna in enumerate(df.columns, 1):
            comprimento = max(
                [len(str(coluna))] + [len(str(v)) for v in df[coluna].head(100)]
            )
            ws.column_dimensions[get_column_letter(idx)].width = min(
                42, max(14, comprimento + 3)
            )
    output = BytesIO()
    wb.save(output)
    return output.getvalue()


try:
    vendas, clientes, produtos = carregar_base()
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
except (OSError, ValueError, sqlite3.Error, KeyError) as exc:
    st.error(f"Não foi possível abrir a base de exemplo: {exc}")
    st.stop()

st.title("Análise comercial")
st.caption(
    "Vendas, produtos e clientes sem compras recentes | Dados fictícios para demonstração"
)
st.info(
    "Este painel usa uma base simulada. Não está conectado ao WinThor nem representa resultados reais de uma empresa.",
    icon="ℹ️",
)

with st.sidebar:
    st.header("Filtros")
    filial = st.selectbox("Filial", sorted(vendas.codfilial.unique().tolist()), index=0)
    fornecedores = sorted(produtos.codfornec.unique().tolist())
    fornecedor = st.selectbox(
        "Fornecedor",
        fornecedores,
        index=(
            fornecedores.index(config["fornecedor"])
            if config["fornecedor"] in fornecedores
            else 0
        ),
    )
    referencia = date.fromisoformat(config["data_referencia"])
    inicio_padrao = referencia - timedelta(days=int(config["dias_sem_compra"]))
    intervalo = st.date_input(
        "Período de vendas", value=(inicio_padrao, referencia), format="DD/MM/YYYY"
    )
    dias = st.number_input(
        "Dias sem compra (clientes)",
        min_value=1,
        max_value=730,
        value=int(config["dias_sem_compra"]),
        step=5,
    )
    st.caption(
        "Para clientes inativos, o período é contado para trás a partir da data final selecionada."
    )

if not isinstance(intervalo, (tuple, list)) or len(intervalo) != 2:
    st.warning("Selecione uma data inicial e uma data final.")
    st.stop()
inicio, fim = intervalo
if inicio > fim:
    st.warning("A data inicial precisa ser anterior à final.")
    st.stop()

# Apenas saídas, notas válidas e vendas (bonificações são mostradas separadamente).
validas = vendas.loc[
    (vendas.codfilial == filial) & vendas.dtcancel.isna() & (vendas.codoper == "S")
].copy()
no_periodo = validas.loc[(validas.dtsaida >= inicio) & (validas.dtsaida <= fim)]
selecao = no_periodo.loc[no_periodo.codfornec == fornecedor]
vendas_pagas = selecao.loc[selecao.condvenda == 1].copy()
bonificacoes = selecao.loc[selecao.condvenda == 5].copy()

st.subheader("Resumo do período")
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Faturamento",
    f"R$ {vendas_pagas.valor.sum():,.2f}".replace(",", "X")
    .replace(".", ",")
    .replace("X", "."),
)
c2.metric("Unidades vendidas", f"{int(vendas_pagas.qt.sum()):,}".replace(",", "."))
c3.metric("Clientes compradores", int(vendas_pagas.codcli.nunique()))
c4.metric("Unidades bonificadas", int(bonificacoes.qt.sum()))

tab_vendas, tab_produtos, tab_clientes, tab_exportar = st.tabs(
    ["Vendas", "Produtos", "Clientes sem compra", "Exportar"]
)

with tab_vendas:
    st.subheader("Evolução das vendas")
    por_dia = vendas_pagas.groupby("dtsaida", as_index=False).agg(
        faturamento=("valor", "sum")
    )
    if por_dia.empty:
        st.info("Não há vendas para os filtros escolhidos.")
    else:
        st.line_chart(
            por_dia.set_index("dtsaida")["faturamento"],
            x_label="Data",
            y_label="Faturamento (R$)",
        )
    st.subheader("Movimentações")
    tabela_vendas = vendas_pagas[
        [
            "dtsaida",
            "numtransvenda",
            "cliente",
            "codprod",
            "descricao",
            "qt",
            "punit",
            "valor",
        ]
    ].rename(
        columns={
            "dtsaida": "Data",
            "numtransvenda": "Nota",
            "cliente": "Cliente",
            "codprod": "Código",
            "descricao": "Produto",
            "qt": "Unidades",
            "punit": "Preço unitário",
            "valor": "Valor (R$)",
        }
    )
    st.dataframe(tabela_vendas, use_container_width=True, hide_index=True)

with tab_produtos:
    st.subheader("Produtos do fornecedor")
    lista_produtos = produtos.loc[
        produtos.codfornec == fornecedor, ["codprod", "descricao"]
    ]
    if lista_produtos.empty:
        st.info("Fornecedor sem produtos cadastrados.")
    else:
        opcoes = dict(zip(lista_produtos.codprod.astype(int), lista_produtos.descricao))
        codigos = list(opcoes)
        escolhido = st.selectbox(
            "Consultar produto",
            codigos,
            format_func=lambda cod: f"{cod} — {opcoes[cod]}",
            index=(
                codigos.index(config["produto"]) if config["produto"] in codigos else 0
            ),
        )
        item = selecao.loc[selecao.codprod == escolhido]
        item_vendas = item.loc[item.condvenda == 1]
        item_bonificacoes = item.loc[item.condvenda == 5]
        embalagem = int(
            produtos.loc[produtos.codprod == escolhido, "unidades_por_caixa"].iloc[0]
            or 0
        )
        unidades = int(item_vendas.qt.sum())
        a, b, c = st.columns(3)
        a.metric("Unidades vendidas", unidades)
        b.metric("Unidades bonificadas", int(item_bonificacoes.qt.sum()))
        c.metric(
            "Caixas equivalentes",
            f"{unidades / embalagem:.2f}".replace(".", ",") if embalagem > 0 else "N/D",
        )
        st.caption(
            f"Embalagem cadastrada: {embalagem} unidades por caixa. Caixas equivalentes não representam necessariamente caixas fechadas."
            if embalagem
            else "Embalagem não cadastrada."
        )
        ranking = (
            vendas_pagas.groupby(["codprod", "descricao"], as_index=False)
            .agg(unidades=("qt", "sum"))
            .sort_values("unidades", ascending=False)
            .head(10)
        )
        st.subheader("Produtos mais vendidos (unidades)")
        if not ranking.empty:
            st.bar_chart(ranking.set_index("descricao")["unidades"], horizontal=True)
        else:
            st.info("Sem vendas no período.")

with tab_clientes:
    st.subheader(f"Clientes sem compras do fornecedor {fornecedor}")
    # A regra segue a consulta do pipeline: NOT EXISTS, incluindo quem nunca comprou.
    # O dia de referência é inclusivo na interface (ao contrário da versão CLI antiga).
    janela_inicio = fim - timedelta(days=int(dias))
    compras_janela = validas.loc[
        (validas.codfornec == fornecedor)
        & (validas.condvenda == 1)
        & (validas.dtsaida >= janela_inicio)
        & (validas.dtsaida <= fim)
    ]
    ativos = set(compras_janela.codcli.unique())
    inativos = clientes.loc[~clientes.codcli.isin(ativos)].copy()
    inativos.columns = ["Código", "Cliente", "Cidade"]
    st.metric("Clientes sem compra na janela", len(inativos))
    st.caption(
        f"Sem vendas entre {janela_inicio:%d/%m/%Y} e {fim:%d/%m/%Y}, incluindo clientes que nunca compraram esse fornecedor."
    )
    st.dataframe(inativos, use_container_width=True, hide_index=True)

with tab_exportar:
    st.subheader("Baixar relatórios filtrados")
    st.caption(
        "Os arquivos abaixo refletem os filtros escolhidos no painel. A atualização não altera os arquivos originais do projeto."
    )
    resumo = pd.DataFrame(
        [
            {
                "Filial": filial,
                "Fornecedor": fornecedor,
                "Início": inicio.isoformat(),
                "Fim": fim.isoformat(),
                "Faturamento": round(float(vendas_pagas.valor.sum()), 2),
                "Unidades vendidas": int(vendas_pagas.qt.sum()),
                "Unidades bonificadas": int(bonificacoes.qt.sum()),
                "Clientes compradores": int(vendas_pagas.codcli.nunique()),
                "Clientes sem compra": len(inativos),
            }
        ]
    )
    st.download_button(
        "Baixar relatório Excel",
        data=excel_bytes(
            {"Resumo": resumo, "Vendas": tabela_vendas, "Clientes sem compra": inativos}
        ),
        file_name="analise_comercial_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.download_button(
        "Baixar vendas em CSV",
        data=csv_bytes(tabela_vendas),
        file_name="vendas_filtradas.csv",
        mime="text/csv",
    )
    st.download_button(
        "Baixar clientes sem compra em CSV",
        data=csv_bytes(inativos),
        file_name="clientes_sem_compra.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Projeto de portfólio • Python + SQL (SQLite) + Excel + Linux • Dados de demonstração"
)
