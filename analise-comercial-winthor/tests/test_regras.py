import sqlite3, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RegrasDeNegocio(unittest.TestCase):
    def test_intervalo_90_dias(self):
        from datetime import date
        self.assertEqual((date(2026,11,17)-date(2026,8,19)).days,90)
    def test_not_exists_inclui_cliente_sem_historico(self):
        c=sqlite3.connect(':memory:')
        c.executescript('CREATE TABLE clientes(id INTEGER); CREATE TABLE vendas(id INTEGER); INSERT INTO clientes VALUES (1),(2); INSERT INTO vendas VALUES (1);')
        self.assertEqual(c.execute('SELECT id FROM clientes WHERE NOT EXISTS (SELECT 1 FROM vendas WHERE vendas.id=clientes.id)').fetchall(),[(2,)])
if __name__=='__main__':unittest.main()
