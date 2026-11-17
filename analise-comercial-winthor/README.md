# Análise comercial de uma distribuidora

Montei esse projeto para organizar três consultas que uso como referência no trabalho: clientes sem compras recentes de um fornecedor, quantidade vendida de um produto e resumo de vendas por fornecedor.

A ideia foi deixar a execução simples. Não faz sentido ter que apagar o banco ou mexer no código toda vez que quero conferir um relatório.

## Como rodar no Windows

1. Instale Python 3 (caso ainda não tenha).
2. Extraia a pasta do projeto.
3. Dê dois cliques em **`ATUALIZAR_RELATORIOS.bat`**.
4. Abra **`relatorios/analise_comercial.xlsx`**. Os CSVs também ficam em `dados/saida`.

Para gerar os relatórios pelo `.bat` não precisa instalar bibliotecas adicionais. As dependências listadas em `requirements.txt` são usadas apenas pelo dashboard. **Feche o Excel antes de atualizar**, caso ele esteja aberto.

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

## Testar o dashboard no navegador

Além dos relatórios em Excel, incluí um painel com filtros de **filial, fornecedor, período e dias sem compra**. Nele dá para conferir faturamento, vendas por dia, produtos mais vendidos, unidades bonificadas, caixas equivalentes e clientes sem compra recente. Também dá para baixar os resultados filtrados em Excel ou CSV.

**Os números são simulados.** O painel lê os arquivos da pasta `dados/entrada`; não acessa o WinThor nem usa dados reais da empresa.

### Windows — jeito mais fácil

1. Clique em **Code → Download ZIP** neste repositório e extraia o arquivo.
2. Instale o Python, caso ainda não tenha.
3. Abra a pasta que contém `dashboard.py`.
4. Dê dois cliques em **`ABRIR_DASHBOARD.bat`**. Na primeira execução, ele instala as bibliotecas necessárias (é preciso internet).
5. O navegador deverá abrir o painel. Se não abrir automaticamente, copie o endereço local indicado no terminal, normalmente `http://localhost:8501`.

Se preferir usar o PowerShell, dentro da pasta do projeto:

```powershell
python -m pip install -r requirements-dashboard.txt
python -m streamlit run dashboard.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dashboard.txt
streamlit run dashboard.py
```

Também é possível usar `bash ABRIR_DASHBOARD.sh` em um ambiente que permita instalar pacotes Python.

### Testar sem instalar nada — publicação online

O repositório inclui `dashboard.py` e `requirements-dashboard.txt`, mas **a versão online só ficará disponível depois de fazer o deploy**. Para publicar gratuitamente no Streamlit Community Cloud:

1. Entre em [share.streamlit.io](https://share.streamlit.io/) e conecte sua conta GitHub.
2. Selecione o repositório `Rafael06vs/analise-comercial-winthor` e a branch `main`.
3. Escolha **`analise-comercial-winthor/dashboard.py`** como arquivo principal, se o repositório mantiver a pasta interna mostrada no GitHub. Se os arquivos estiverem na raiz, use `dashboard.py`.
4. O arquivo `requirements.txt` já inclui as dependências do dashboard; mantenha-o na mesma pasta do `dashboard.py`.
5. Faça o deploy, teste o endereço gerado e só então adicione o link público ao início deste README.

Não coloque dados internos, senhas ou exportações reais do ERP no repositório público.

### Como os cálculos funcionam

- **Faturamento:** apenas notas não canceladas, movimentação de saída (`S`) e condição de venda `1`.
- **Bonificações:** condição `5`, contabilizadas em unidades, sem somar ao faturamento.
- **Caixas equivalentes:** unidades vendidas divididas pela quantidade de unidades por caixa cadastrada.
- **Clientes sem compra:** todos os clientes da base sem venda do fornecedor na janela escolhida, inclusive quem nunca comprou dele.
- **Período:** datas inicial e final inclusivas no painel. O recorte de clientes sem compra usa a data final como referência.

O pipeline original continua funcionando com `ATUALIZAR_RELATORIOS.bat`, independentemente do dashboard.


## Por que o VS Code mostra caracteres estranhos?

`dados/analise.db` (SQLite) e `relatorios/analise_comercial.xlsx` (Excel) são arquivos **binários**. Não devem ser abertos no editor de texto do VS Code. Abra o `.xlsx` no Microsoft Excel ou LibreOffice; para explorar um `.db`, use um visualizador SQLite. A versão atual executa as consultas em memória e **não precisa** do arquivo `analise.db` antigo.

## Atualizar e testar

- Windows: execute `ATUALIZAR_RELATORIOS.bat` para gerar os CSVs e o Excel.
- Dashboard: execute `ABRIR_DASHBOARD.bat` para abrir o Streamlit no navegador.
- Terminal: `python scripts/analisar.py` e `python -m unittest discover -s tests -v`.
- Linux: `bash scripts/rodar.sh` e `bash ABRIR_DASHBOARD.sh`.

O dashboard usa dados simulados. Para testar online, publique `dashboard.py` no Streamlit Community Cloud e informe o link aqui.
