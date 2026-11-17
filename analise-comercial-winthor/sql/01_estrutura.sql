-- Banco SQLite local, usado apenas com dados fictícios.
-- A execução do analisador cria uma base nova em memória.

CREATE TABLE clientes (
    codcli INTEGER PRIMARY KEY,
    cliente TEXT NOT NULL,
    cidade TEXT NOT NULL
);

CREATE TABLE produtos (
    codprod INTEGER PRIMARY KEY,
    codfab TEXT,
    descricao TEXT NOT NULL,
    codfornec INTEGER NOT NULL,
    unidades_por_caixa INTEGER
);

CREATE TABLE notas (
    numtransvenda INTEGER PRIMARY KEY,
    codcli INTEGER NOT NULL,
    codfilial INTEGER NOT NULL,
    dtsaida TEXT NOT NULL,
    condvenda INTEGER NOT NULL,
    dtcancel TEXT,
    FOREIGN KEY (codcli) REFERENCES clientes (codcli)
);

CREATE TABLE movimentos (
    id INTEGER PRIMARY KEY,
    numtransvenda INTEGER NOT NULL,
    codprod INTEGER NOT NULL,
    codoper TEXT NOT NULL,
    qt INTEGER NOT NULL,
    punit REAL NOT NULL,
    FOREIGN KEY (numtransvenda) REFERENCES notas (numtransvenda),
    FOREIGN KEY (codprod) REFERENCES produtos (codprod)
);

CREATE INDEX idx_notas_data
    ON notas (dtsaida, codfilial, condvenda);

CREATE INDEX idx_mov_prod
    ON movimentos (codprod, numtransvenda);
