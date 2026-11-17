from pathlib import Path
from datetime import date, timedelta
import csv
import json
import sqlite3
import sys
import zipfile
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ENTRADA = ROOT / 'dados' / 'entrada'
SAIDA = ROOT / 'dados' / 'saida'
SAIDA.mkdir(parents=True, exist_ok=True)


def ler_config():
    with (ROOT / 'config.json').open(encoding='utf-8') as f:
        c = json.load(f)
    data = date.fromisoformat(c['data_referencia'])
    inicio = date.fromisoformat(c['inicio_produto'])
    fim = date.fromisoformat(c['fim_produto'])
    if inicio > fim:
        raise ValueError('inicio_produto deve ser anterior ou igual a fim_produto')
    return c, data, inicio, fim


def exportar_csv(nome, cabecalho, linhas):
    with (SAIDA / nome).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(cabecalho)
        w.writerows(linhas)
    print(f'  OK: {nome} ({len(linhas)} linhas)')


def coluna_excel(n):
    s = ''
    while n:
        n, resto = divmod(n - 1, 26)
        s = chr(65 + resto) + s
    return s


def gerar_excel(tabelas):
    # XLSX padrão Office Open XML, sem bibliotecas externas.
    from xml.sax.saxutils import quoteattr
    arquivo = ROOT / 'relatorios' / 'analise_comercial.xlsx'
    arquivo.parent.mkdir(exist_ok=True)
    tipos = 'application/vnd.openxmlformats-officedocument.spreadsheetml.'
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                     '<Default Extension="xml" ContentType="application/xml"/>',
                     f'<Override PartName="/xl/workbook.xml" ContentType="{tipos}sheet.main+xml"/>',
                     f'<Override PartName="/xl/styles.xml" ContentType="{tipos}styles+xml"/>']
    for i in range(1, len(tabelas) + 1):
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="{tipos}worksheet+xml"/>')
    content_types.append('</Types>')
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    sheets = ''.join(f'<sheet name={quoteattr(nome)} sheetId="{i}" r:id="rId{i}"/>' for i, (nome, _, _) in enumerate(tabelas, 1))
    workbook = f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheets}</sheets></workbook>'
    rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(tabelas) + 1)) + f'<Relationship Id="rId{len(tabelas)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'
    styles = f'''<styleSheet xmlns="{ns}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF17365D"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="1" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs></styleSheet>'''
    with zipfile.ZipFile(arquivo, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ''.join(content_types))
        z.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', workbook)
        z.writestr('xl/_rels/workbook.xml.rels', rels)
        z.writestr('xl/styles.xml', styles)
        for i, (nome, cab, dados) in enumerate(tabelas, 1):
            linhas_xml = []
            for rn, valores in enumerate([cab] + dados, 1):
                celulas = []
                for cn, valor in enumerate(valores, 1):
                    ref = f'{coluna_excel(cn)}{rn}'
                    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                        celulas.append(f'<c r="{ref}"' + (' s="1"' if rn == 1 else '') + f'><v>{valor}</v></c>')
                    else:
                        celulas.append(f'<c r="{ref}" t="inlineStr"' + (' s="1"' if rn == 1 else '') + f'><is><t>{escape(str(valor if valor is not None else ""))}</t></is></c>')
                linhas_xml.append(f'<row r="{rn}">' + ''.join(celulas) + '</row>')
            largura = ''.join(f'<col min="{j}" max="{j}" width="{min(40, max(15, len(str(c))*1.5))}" customWidth="1"/>' for j, c in enumerate(cab, 1))
            ultimo = f'{coluna_excel(len(cab))}{max(1, len(dados)+1)}'
            sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="{ns}"><dimension ref="A1:{ultimo}"/><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>{largura}</cols><sheetData>{"".join(linhas_xml)}</sheetData><autoFilter ref="A1:{ultimo}"/></worksheet>'
            z.writestr(f'xl/worksheets/sheet{i}.xml', sheet)
    print(f'  OK: {arquivo.relative_to(ROOT)}')


def executar():
    """Executa as consultas sobre uma base temporária, sem tabelas duplicadas."""
    cfg, referencia, inicio_produto, fim_produto = ler_config()
    filial = int(cfg["filial"])
    fornecedor = int(cfg["fornecedor"])
    produto = int(cfg["produto"])
    dias = int(cfg["dias_sem_compra"])
    if dias <= 0:
        raise ValueError("dias_sem_compra precisa ser positivo")

    inicio_clientes = (referencia - timedelta(days=dias)).isoformat()
    fim_clientes = referencia.isoformat()  # limite exclusivo
    fim_produto_exclusivo = (fim_produto + timedelta(days=1)).isoformat()

    # O banco é recriado em memória em cada execução. Nenhum .db precisa ser apagado.
    with sqlite3.connect(":memory:") as conexao:
        conexao.execute("PRAGMA foreign_keys = ON")
        estrutura = (ROOT / "sql" / "01_estrutura.sql").read_text(encoding="utf-8")
        conexao.executescript(estrutura)

        for tabela in ("clientes", "produtos", "notas", "movimentos"):
            caminho = ENTRADA / f"{tabela}.csv"
            with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
                leitor = csv.DictReader(arquivo)
                colunas = leitor.fieldnames
                registros = list(leitor)

            if not colunas:
                raise ValueError(f"Arquivo sem cabeçalho: {caminho}")
            if not registros:
                continue

            marcadores = ", ".join("?" for _ in colunas)
            nomes_colunas = ", ".join(colunas)
            consulta = f"INSERT INTO {tabela} ({nomes_colunas}) VALUES ({marcadores})"
            valores = [
                [registro[coluna] or None for coluna in colunas]
                for registro in registros
            ]
            conexao.executemany(consulta, valores)

        sql_clientes = """
            SELECT c.codcli, c.cliente, c.cidade
            FROM clientes AS c
            WHERE NOT EXISTS (
                SELECT 1
                FROM notas AS n
                JOIN movimentos AS m ON m.numtransvenda = n.numtransvenda
                JOIN produtos AS p ON p.codprod = m.codprod
                WHERE n.codcli = c.codcli
                  AND n.codfilial = ?
                  AND p.codfornec = ?
                  AND n.condvenda = 1
                  AND n.dtcancel IS NULL
                  AND m.codoper = 'S'
                  AND n.dtsaida >= ?
                  AND n.dtsaida < ?
            )
            ORDER BY c.cliente
        """

        sql_produto = """
            SELECT
                p.codprod,
                p.descricao,
                SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END)
                    AS unidades_vendidas,
                SUM(CASE WHEN n.condvenda = 5 THEN m.qt ELSE 0 END)
                    AS unidades_bonificadas,
                ROUND(SUM(CASE WHEN n.condvenda = 1 THEN m.qt * m.punit ELSE 0 END), 2)
                    AS faturamento,
                CASE WHEN p.unidades_por_caixa > 0 THEN
                    ROUND(
                        1.0 * SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END)
                        / p.unidades_por_caixa,
                        2
                    )
                END AS caixas_equivalentes
            FROM notas AS n
            JOIN movimentos AS m ON m.numtransvenda = n.numtransvenda
            JOIN produtos AS p ON p.codprod = m.codprod
            WHERE p.codprod = ?
              AND n.codfilial = ?
              AND n.dtcancel IS NULL
              AND m.codoper = 'S'
              AND n.condvenda IN (1, 5)
              AND n.dtsaida >= ?
              AND n.dtsaida < ?
            GROUP BY p.codprod, p.descricao, p.unidades_por_caixa
        """

        sql_resumo = """
            SELECT
                p.codfornec,
                COUNT(DISTINCT n.numtransvenda) AS notas,
                SUM(m.qt) AS unidades,
                ROUND(SUM(m.qt * m.punit), 2) AS faturamento
            FROM notas AS n
            JOIN movimentos AS m ON m.numtransvenda = n.numtransvenda
            JOIN produtos AS p ON p.codprod = m.codprod
            WHERE n.codfilial = ?
              AND n.dtcancel IS NULL
              AND n.condvenda = 1
              AND m.codoper = 'S'
              AND n.dtsaida >= ?
              AND n.dtsaida < ?
            GROUP BY p.codfornec
            ORDER BY faturamento DESC
        """

        consultas = [
            (
                "clientes_sem_compra_658.csv",
                "Clientes sem compra",
                sql_clientes,
                (filial, fornecedor, inicio_clientes, fim_clientes),
            ),
            (
                "produto_20690.csv",
                "Produto analisado",
                sql_produto,
                (produto, filial, inicio_produto.isoformat(), fim_produto_exclusivo),
            ),
            (
                "resumo_fornecedor.csv",
                "Resumo fornecedor",
                sql_resumo,
                (filial, inicio_clientes, fim_clientes),
            ),
        ]

        tabelas = []
        print("Atualizando relatórios...")
        for nome_arquivo, nome_aba, consulta, parametros in consultas:
            cursor = conexao.execute(consulta, parametros)
            cabecalho = [coluna[0] for coluna in cursor.description]
            linhas = cursor.fetchall()
            exportar_csv(nome_arquivo, cabecalho, linhas)
            tabelas.append((nome_aba, cabecalho, linhas))

        gerar_excel(tabelas)
        print("Concluído. Notas canceladas e bonificações não entram no faturamento.")


if __name__ == "__main__":
    try:
        executar()
    except (OSError, sqlite3.Error, ValueError, KeyError) as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        sys.exit(1)
