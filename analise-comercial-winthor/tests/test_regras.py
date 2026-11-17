"""Testes das regras de negócio utilizadas nas consultas."""

import sqlite3
import unittest
from datetime import date


class RegrasDeNegocio(unittest.TestCase):
    def test_intervalo_90_dias(self):
        inicio = date(2026, 8, 19)
        referencia = date(2026, 11, 17)
        self.assertEqual((referencia - inicio).days, 90)

    def test_not_exists_inclui_cliente_sem_historico(self):
        with sqlite3.connect(":memory:") as conexao:
            conexao.executescript(
                """
                CREATE TABLE clientes (id INTEGER);
                CREATE TABLE vendas (id INTEGER);
                INSERT INTO clientes VALUES (1), (2);
                INSERT INTO vendas VALUES (1);
                """
            )
            resultado = conexao.execute(
                """
                SELECT id
                FROM clientes
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM vendas
                    WHERE vendas.id = clientes.id
                )
                """
            ).fetchall()
        self.assertEqual(resultado, [(2,)])


if __name__ == "__main__":
    unittest.main()
