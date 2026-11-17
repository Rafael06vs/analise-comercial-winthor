-- Clientes cadastrados sem venda válida do fornecedor 658 nos 90 dias anteriores a 17/11/2026.
-- NOT EXISTS inclui quem nunca comprou. Bonificação não conta como compra.
SELECT c.codcli, c.cliente, c.cidade
FROM clientes c
WHERE NOT EXISTS (
  SELECT 1 FROM notas n
  JOIN movimentos m ON m.numtransvenda = n.numtransvenda
  JOIN produtos p ON p.codprod = m.codprod
  WHERE n.codcli = c.codcli AND n.codfilial = 1
    AND p.codfornec = 658 AND n.condvenda = 1
    AND n.dtcancel IS NULL AND m.codoper = 'S'
    AND n.dtsaida >= '2026-08-19' AND n.dtsaida < '2026-11-17'
)
ORDER BY c.cliente;

-- Produto 20690, de 06/11 a 17/11, inclusive; bonificação separada.
SELECT p.codprod, p.descricao,
 SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END) unidades_vendidas,
 SUM(CASE WHEN n.condvenda = 5 THEN m.qt ELSE 0 END) unidades_bonificadas,
 ROUND(SUM(CASE WHEN n.condvenda = 1 THEN m.qt*m.punit ELSE 0 END),2) faturamento,
 CASE WHEN p.unidades_por_caixa > 0 THEN
 ROUND(1.0*SUM(CASE WHEN n.condvenda = 1 THEN m.qt ELSE 0 END)/p.unidades_por_caixa,2)
 END caixas_equivalentes
FROM notas n JOIN movimentos m ON m.numtransvenda = n.numtransvenda
JOIN produtos p ON p.codprod = m.codprod
WHERE p.codprod = 20690 AND n.codfilial = 1 AND n.dtcancel IS NULL
 AND m.codoper = 'S' AND n.condvenda IN (1,5)
 AND n.dtsaida >= '2026-11-06' AND n.dtsaida < '2026-11-18'
GROUP BY p.codprod, p.descricao, p.unidades_por_caixa;
