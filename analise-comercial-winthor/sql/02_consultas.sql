-- Clientes sem venda válida do fornecedor 658 nos 90 dias anteriores a 17/11/2026.
-- NOT EXISTS também inclui clientes que nunca compraram.
-- Bonificações não são consideradas compras.
SELECT
    c.codcli,
    c.cliente,
    c.cidade
FROM clientes AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM notas AS n
    JOIN movimentos AS m
        ON m.numtransvenda = n.numtransvenda
    JOIN produtos AS p
        ON p.codprod = m.codprod
    WHERE n.codcli = c.codcli
      AND n.codfilial = 1
      AND p.codfornec = 658
      AND n.condvenda = 1
      AND n.dtcancel IS NULL
      AND m.codoper = 'S'
      AND n.dtsaida >= '2026-08-19'
      AND n.dtsaida < '2026-11-17'
)
ORDER BY c.cliente;

-- Produto 20690 entre 06/11 e 17/11, inclusive.
-- Bonificações são apresentadas separadamente.
SELECT
    p.codprod,
    p.descricao,
    SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END)
        AS unidades_vendidas,
    SUM(CASE WHEN n.condvenda = 5 THEN m.qt ELSE 0 END)
        AS unidades_bonificadas,
    ROUND(
        SUM(CASE WHEN n.condvenda = 1 THEN m.qt * m.punit ELSE 0 END),
        2
    ) AS faturamento,
    CASE
        WHEN p.unidades_por_caixa > 0 THEN
            ROUND(
                1.0 * SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END)
                / p.unidades_por_caixa,
                2
            )
    END AS caixas_equivalentes
FROM notas AS n
JOIN movimentos AS m
    ON m.numtransvenda = n.numtransvenda
JOIN produtos AS p
    ON p.codprod = m.codprod
WHERE p.codprod = 20690
  AND n.codfilial = 1
  AND n.dtcancel IS NULL
  AND m.codoper = 'S'
  AND n.condvenda IN (1, 5)
  AND n.dtsaida >= '2026-11-06'
  AND n.dtsaida < '2026-11-18'
GROUP BY p.codprod, p.descricao, p.unidades_por_caixa;
