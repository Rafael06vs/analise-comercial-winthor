# Análise comercial de uma distribuidora

Montei esse projeto para organizar três consultas que uso como referência no trabalho: clientes sem compras recentes de um fornecedor, quantidade vendida de um produto e resumo de vendas por fornecedor.

A ideia foi deixar a execução simples. Não faz sentido ter que apagar o banco ou mexer no código toda vez que quero conferir um relatório.

## Como rodar no Windows

1. Instale Python 3 (caso ainda não tenha).
2. Extraia a pasta do projeto.
3. Dê dois cliques em **`ATUALIZAR_RELATORIOS.bat`**.
4. Abra **`relatorios/analise_comercial.xlsx`**. Os CSVs também ficam em `dados/saida`.

Não precisa instalar nada com `pip`. O script funciona mesmo se já tiver sido executado antes. **Feche o Excel antes de atualizar**, caso ele esteja aberto.

Se preferir o terminal:

```powershell
python scripts/analisar.py
```

## Como rodar no Linux

```bash
python3 scripts/analisar.py
```

## O que o projeto faz

- Lê os arquivos de exemplo em `dados/entrada`.
- Cria um banco SQLite temporário a cada execução. Isso evita o erro `table clientes already exists` e impede duplicação por reexecução.
- Calcula clientes sem compras do fornecedor na janela definida, inclusive os que nunca compraram.
- Separa unidades vendidas e bonificadas do produto escolhido.
- Gera um resumo de faturamento por fornecedor, sem bonificações ou notas canceladas.
- Atualiza três CSVs e um Excel com abas e filtros.

## Configurações

As configurações estão em `config.json`. O exemplo acompanha a filial 1, fornecedor 658, produto 20690, referência em 17/11/2026 e intervalo de 90 dias. **Não precisa alterar código Python ou SQL** para gerar os relatórios novamente. Se quiser analisar outro período ou produto, pode mudar apenas os valores do arquivo de configuração.

## Organização

- `dados/entrada`: dados fictícios de clientes, produtos, notas e movimentações.
- `dados/saida`: relatórios CSV gerados automaticamente.
- `relatorios/analise_comercial.xlsx`: relatório Excel atualizado em cada execução.
- `scripts/analisar.py`: processamento dos dados.
- `scripts/gerar_dados.py`: recria a base fictícia, se você quiser começar do zero.
- `sql/`: exemplos de estrutura e consultas SQL.
- `tests/`: testes das regras de negócio.

## Regras de negócio

Considero venda válida a movimentação de saída (`CODOPER = 'S'`), condição 1, nota não cancelada e filial selecionada. Bonificação (condição 5) é apresentada separadamente e não entra no faturamento. A conversão para caixas depende da quantidade de unidades por caixa cadastrada na base de exemplo.

Os dados são **fictícios**. O banco SQLite serve para simular a análise; o WinThor real utiliza Oracle. Este projeto não acessa o ERP nem expõe dados de clientes reais.

## Próxima etapa

Evoluir a análise com exportações anonimizadas e indicadores de logística, sem comprometer informações internas da empresa.
