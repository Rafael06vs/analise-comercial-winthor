from pathlib import Path
import csv, sqlite3
ROOT=Path(__file__).resolve().parents[1]
ENTRADA=ROOT/'dados'/'entrada'; SAIDA=ROOT/'dados'/'saida'
SAIDA.mkdir(parents=True,exist_ok=True)
DB=ROOT/'dados'/'analise.db'
with sqlite3.connect(DB) as con:
    con.executescript((ROOT/'sql'/'01_estrutura.sql').read_text(encoding='utf-8'))
    for nome in ('clientes','produtos','notas','movimentos'):
        with (ENTRADA/f'{nome}.csv').open(encoding='utf-8',newline='') as f:
            linhas=list(csv.DictReader(f))
        colunas=list(linhas[0])
        sql=f"INSERT INTO {nome} ({','.join(colunas)}) VALUES ({','.join('?' for _ in colunas)})"
        con.executemany(sql,[[r[c] if r[c]!='' else None for c in colunas] for r in linhas])
    texto=(ROOT/'sql'/'02_consultas.sql').read_text(encoding='utf-8')
    texto='\n'.join(l for l in texto.splitlines() if not l.lstrip().startswith('--'))
    consultas=[q.strip() for q in texto.split(';') if q.strip()]
    for arquivo,consulta in zip(('clientes_sem_compra_658.csv','produto_20690.csv'),consultas):
        cursor=con.execute(consulta)
        with (SAIDA/arquivo).open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow([c[0] for c in cursor.description]);w.writerows(cursor.fetchall())
        print('Gerado:',arquivo)
    cur=con.execute("""SELECT p.codfornec, COUNT(DISTINCT n.numtransvenda) notas,
      SUM(m.qt) unidades, ROUND(SUM(m.qt*m.punit),2) faturamento
      FROM notas n JOIN movimentos m ON m.numtransvenda=n.numtransvenda
      JOIN produtos p ON p.codprod=m.codprod
      WHERE n.codfilial=1 AND n.dtcancel IS NULL AND n.condvenda=1 AND m.codoper='S'
      AND n.dtsaida>='2026-08-19' AND n.dtsaida<'2026-11-17'
      GROUP BY p.codfornec ORDER BY faturamento DESC""")
    with (SAIDA/'resumo_fornecedor.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow([c[0] for c in cur.description]);w.writerows(cur.fetchall())
print('Conferência: bonificações e cancelamentos não entram no faturamento.')
