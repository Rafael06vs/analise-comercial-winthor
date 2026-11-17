from pathlib import Path
import csv, random, datetime
BASE = Path(__file__).resolve().parents[1] / 'dados' / 'entrada'
BASE.mkdir(parents=True, exist_ok=True)
rng = random.Random(658)
def salvar(nome, cab, linhas):
    with (BASE / nome).open('w', newline='', encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(cab); w.writerows(linhas)
clientes=[(12000+i, f'Cliente exemplo {i:03d}', rng.choice(['São Paulo','Guarulhos','Osasco','Santo André','Jundiaí'])) for i in range(1,81)]
produtos=[(20690,'20690','Pão de queijo tradicional',658,12),(20691,'20691','Pão de queijo coquetel',658,10),(20692,'20692','Waffle congelado',658,8),(30185,'30185','Batata congelada',7,6),(30186,'30186','Vegetais congelados',7,10)]
notas=[]; mov=[]; trans=100000; mid=1
for dia in range(150):
    data=datetime.date(2026,7,1)+datetime.timedelta(days=dia)
    if data>datetime.date(2026,11,17): break
    for _ in range(rng.randint(1,8)):
        cliente=rng.choice(clientes)[0]
        prod=rng.choice(produtos)
        trans+=1
        cond=5 if rng.random()<.08 else 1
        cancel=data.isoformat() if rng.random()<.025 else ''
        notas.append((trans,cliente,1,data.isoformat(),cond,cancel))
        mov.append((mid,trans,prod[0],'S',rng.randint(1,30),round(rng.uniform(8,45),2)));mid+=1
salvar('clientes.csv',['codcli','cliente','cidade'],clientes)
salvar('produtos.csv',['codprod','codfab','descricao','codfornec','unidades_por_caixa'],produtos)
salvar('notas.csv',['numtransvenda','codcli','codfilial','dtsaida','condvenda','dtcancel'],notas)
salvar('movimentos.csv',['id','numtransvenda','codprod','codoper','qt','punit'],mov)
print(f'Dados fictícios: {len(clientes)} clientes, {len(notas)} notas.')
