import json
import os
import sqlite3
from pathlib import Path

DB = Path(os.environ.get('APARTAMENTO_DB', Path(__file__).parent / 'dados' / 'apartamento.db'))


def conectar():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB, timeout=20)
    conn.execute('CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, conteudo TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS aportes (mes TEXT PRIMARY KEY, valor REAL NOT NULL CHECK(valor >= 0), nota TEXT NOT NULL)')
    return conn


def carregar(padrao):
    with conectar() as conn:
        row = conn.execute('SELECT conteudo FROM config WHERE id=1').fetchone()
    return {**padrao, **(json.loads(row[0]) if row else {})}


def salvar(config):
    with conectar() as conn:
        conn.execute('INSERT OR REPLACE INTO config VALUES (1, ?)', (json.dumps(config),))


def registrar(mes, valor, nota):
    with conectar() as conn:
        conn.execute('INSERT OR REPLACE INTO aportes VALUES (?, ?, ?)', (mes, valor, nota))


def historico():
    with conectar() as conn:
        return conn.execute('SELECT mes, valor, nota FROM aportes ORDER BY mes').fetchall()


def excluir(mes):
    with conectar() as conn:
        conn.execute('DELETE FROM aportes WHERE mes=?', (mes,))
