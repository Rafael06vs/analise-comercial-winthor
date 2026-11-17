# Análise comercial de uma distribuidora

**SQL · Python · SQLite · Excel · Linux · Streamlit**

Criei este projeto a partir de algumas situações que aparecem na rotina comercial de uma distribuidora: descobrir quais clientes deixaram de comprar uma marca, conferir a quantidade vendida de um produto e entender o faturamento por fornecedor.

O maior cuidado foi definir **o que realmente conta como venda**. Uma nota cancelada não pode entrar no resultado, bonificação não é faturamento e quantidade em unidades não é a mesma coisa que quantidade em caixas.

O projeto usa **dados fictícios**, com estrutura inspirada em consultas que faço no WinThor. Não existe conexão com o ERP ou utilização de informações reais da empresa.

## O que dá para analisar

- **Clientes sem compras recentes:** identifica clientes que não compraram produtos de um fornecedor no período definido, incluindo aqueles que nunca compraram essa marca.
- **Vendas por produto:** consulta unidades vendidas, unidades bonificadas, faturamento e caixas equivalentes.
- **Resumo por fornecedor:** consolida quantidade de notas, unidades e faturamento de vendas válidas.
- **Dashboard:** permite filtrar filial, fornecedor e período, acompanhar indicadores e baixar resultados em CSV ou Excel.

No exemplo inicial, utilizei a **filial 1**, o **fornecedor 658** e o **produto 20690**. A consulta do produto considera **06/11/2026 a 17/11/2026**; a análise de clientes utiliza uma janela de **90 dias**. Esses parâmetros podem ser ajustados no `config.json` para os relatórios e nos filtros do dashboard.

## Como funciona

1. Os arquivos CSV de `dados/entrada` representam clientes, produtos, notas e movimentações.
2. O Python carrega os dados em um banco **SQLite temporário, em memória**.
3. As consultas aplicam as regras comerciais e calculam os indicadores.
4. O processamento gera arquivos CSV em `dados/saida` e um relatório Excel em `relatorios/analise_comercial.xlsx`.
5. O dashboard em Streamlit apresenta os dados no navegador, com filtros e exportação.

O banco é recriado a cada execução, evitando o erro de tabela já existente. O arquivo antigo `analise.db` não é necessário para executar a versão atual.

## Testar no Windows

É necessário ter o **Python instalado**.

1. Clique em **Code → Download ZIP** neste repositório e extraia os arquivos.
2. Entre na pasta que contém `dashboard.py`, `config.json` e os arquivos `.bat`.
3. Para atualizar os relatórios, dê dois cliques em **`ATUALIZAR_RELATORIOS.bat`**.
4. Para abrir o painel interativo, dê dois cliques em **`ABRIR_DASHBOARD.bat`**.
5. Abra no navegador o endereço indicado pelo terminal, normalmente `http://localhost:8501`.

Na primeira abertura do dashboard, o arquivo `.bat` pode precisar instalar as bibliotecas, portanto é necessário acesso à internet. Caso apareça um erro de compatibilidade, utilize uma versão estável do Python compatível com as dependências do projeto, como Python 3.12 ou 3.13.

### Executar pelo terminal (PowerShell)

Na pasta do projeto:

```powershell
python -m pip install -r requirements-dashboard.txt
python scripts/analisar.py
python -m streamlit run dashboard.py
```

O processamento dos relatórios também pode ser executado separadamente, sem abrir o dashboard:

```powershell
python scripts/analisar.py
```

## Testar no Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dashboard.txt
python scripts/analisar.py
python -m streamlit run dashboard.py
```

Também existem scripts de execução: `scripts/rodar.sh` e `ABRIR_DASHBOARD.sh`.

## Testar pelo navegador, sem instalar nada

O código está preparado para publicação no **Streamlit Community Cloud**, mas o GitHub, sozinho, não executa o dashboard. O link público só poderá ser adicionado aqui depois que a aplicação for publicada e testada.

Para fazer o deploy:

1. Acesse [Streamlit Community Cloud](https://share.streamlit.io/) e conecte o GitHub.
2. Selecione o repositório `Rafael06vs/analise-comercial-winthor` e a branch `main`.
3. Indique o arquivo principal: `analise-comercial-winthor/dashboard.py` se o projeto continuar dentro da pasta interna; caso esteja na raiz, use `dashboard.py`.
4. Verifique se o `requirements.txt` está na mesma pasta do dashboard e contém as dependências necessárias.
5. Publique, teste o endereço gerado e adicione o link nesta seção.

**Link do dashboard:** ainda não publicado.

## Regras consideradas nas consultas

| Regra | Tratamento |
| --- | --- |
| Filial | Apenas a filial selecionada |
| Saída de mercadoria | `codoper = 'S'` |
| Venda | `condvenda = 1` |
| Bonificação | `condvenda = 5`, separada do faturamento |
| Nota cancelada | Excluída das análises |
| Clientes sem compra | Consulta com `NOT EXISTS`, incluindo clientes sem histórico da marca |
| Caixas equivalentes | Unidades vendidas ÷ unidades por caixa cadastradas |

A quantidade em caixas é **equivalente**, podendo resultar em valor fracionado. Não deve ser confundida com a quantidade física de caixas fechadas expedidas.

## Arquivos principais

```text
analise-comercial-winthor/
├── dados/
│   ├── entrada/               # CSVs fictícios
│   └── saida/                 # Relatórios CSV
├── relatorios/
│   └── analise_comercial.xlsx
├── scripts/
│   ├── analisar.py
│   ├── gerar_dados.py
│   └── rodar.sh
├── sql/
│   ├── 01_estrutura.sql
│   └── 02_consultas.sql
├── tests/
│   └── test_regras.py
├── dashboard.py
├── config.json
├── ATUALIZAR_RELATORIOS.bat
├── ABRIR_DASHBOARD.bat
├── ABRIR_DASHBOARD.sh
├── requirements.txt
└── requirements-dashboard.txt
```

## Testes

Para executar os testes automatizados:

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam regras básicas, como o intervalo de 90 dias e a inclusão de clientes sem histórico de compra na consulta com `NOT EXISTS`.

## Observações

- O arquivo `.xlsx` deve ser aberto no **Excel**, e não como texto no VS Code.
- O arquivo `.db` é um banco SQLite binário. A versão atual usa banco temporário em memória.
- O relatório Excel é atualizado pelo processamento; o dashboard é uma interface separada que lê a base fictícia.
- O projeto é um exercício de portfólio, não um sistema conectado à operação real.

