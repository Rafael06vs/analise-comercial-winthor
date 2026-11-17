# Análise comercial de uma distribuidora | SQL, Linux e Excel

Esse projeto nasceu de uma dúvida que aparece muito no dia a dia de uma distribuidora: **quem deixou de comprar uma marca, quais produtos giraram e quanto isso representa em caixas?**

Em vez de começar por um dashboard, comecei pelas consultas. O ponto mais trabalhoso foi definir o que conta como venda: notas faturadas, sem cancelamentos, sem devoluções e com bonificação separada. Outra decisão importante: cliente que nunca comprou uma marca **também** entra na lista de clientes sem compras recentes.

## O que tem aqui

- `sql/01_estrutura.sql`: tabelas simplificadas, inspiradas em campos do WinThor, mas **não** é uma cópia do banco da empresa.
- `sql/02_consultas.sql`: consultas de clientes sem compras de um fornecedor, quantidade vendida por produto e resumo por fornecedor.
- `scripts/gerar_dados.py`: dados inventados, reproduzíveis.
- `scripts/analisar.py`: importa CSV para SQLite, roda consultas e exporta os resultados.
- `scripts/rodar.sh`: execução no Linux, com log e tratamento de erro.
- `relatorios/analise_comercial.xlsx`: relatório Excel com abas de clientes sem compra, giro e conferência.

## Regras de negócio que usei

- Filial `1`.
- Fornecedor `658` como exemplo de marca analisada.
- Produto `20690` como exemplo de consulta pontual.
- Data de referência **17/11/2026**; janela de 90 dias: **19/08/2026 a 16/11/2026**, inclusive. A data de referência é o dia seguinte ao fim da janela.
- Venda = `CONDVENDA = 1` e `CODOPER = 'S'`, com nota não cancelada.
- Bonificação (`CONDVENDA = 5`) é mostrada à parte, não entra em faturamento.
- Cliente sem compras = **qualquer cliente cadastrado** sem venda válida do fornecedor na janela, inclusive quem nunca comprou.
- `QT` é quantidade de movimentação. Caixas são calculadas apenas se houver um fator de conversão conhecido; não presumo que `QT` já seja caixa.

## Rodando no Ubuntu / WSL

```bash
sudo apt update
sudo apt install -y python3 python3-venv sqlite3
cd analise-comercial-winthor
bash scripts/rodar.sh
python3 -m unittest discover -s tests -v
```

O script gera os CSVs em `dados/saida/`. O Excel de exemplo já acompanha o repositório; para atualizar o Excel a partir dos CSVs, importe as tabelas no Excel (Dados > De Texto/CSV) ou utilize o script de geração da pasta `scripts` no ambiente Python com `artifact-tool` instalado.

## Conferência que faço antes de confiar no resultado

1. Verificar se a mesma nota não foi duplicada por um JOIN.
2. Comparar o total de unidades com o total da rotina do ERP.
3. Confirmar se o código é `CODPROD` ou `CODFAB`.
4. Conferir cancelamentos, devoluções e bonificações separadamente.
5. Conferir a unidade de medida e o fator de caixa antes de chamar quantidade de “caixas”.

## Limites

Os dados são **100% fictícios**. O banco local é SQLite para facilitar a execução no GitHub; no ambiente real, o WinThor usa Oracle e as consultas precisam ser adaptadas e validadas conforme a versão e as tabelas existentes. Não há credenciais, nomes de clientes reais nem acesso ao ERP neste projeto.

## Próximos passos

Pretendo conectar uma exportação anonimizada do ERP, incluir custo de frete por rota e medir quais clientes sem compras recentes foram recuperados após contato comercial.
