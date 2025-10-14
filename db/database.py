# db/database.py

import sqlite3
from pathlib import Path

DB_PATH = Path("ponto.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# db/database.py (função init_db atualizada)

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                entrada TEXT NOT NULL,
                saida TEXT,
                inicio_intervalo TEXT,
                fim_intervalo TEXT,
                situacao_dia TEXT DEFAULT 'Trabalho',
                observacoes TEXT
            )
        ''')
        
        # Adiciona colunas em bancos existentes (compatibilidade)
        for col in ["inicio_intervalo", "fim_intervalo"]:
            try:
                conn.execute(f"ALTER TABLE registros ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass  # Já existe

        # Migração de 'status' → 'situacao_dia' (mantido)
        try:
            cur = conn.execute("PRAGMA table_info(registros)")
            colunas = [col[1] for col in cur.fetchall()]
            if "status" in colunas and "situacao_dia" not in colunas:
                conn.execute("ALTER TABLE registros ADD COLUMN situacao_dia TEXT DEFAULT 'Trabalho'")
                conn.execute("UPDATE registros SET situacao_dia = status WHERE status IS NOT NULL")
        except Exception:
            pass

        conn.commit()

# ✅ Esta é a função que está faltando!
def buscar_registros_por_colaborador(nome: str, periodo: str = "todos"):
    """
    Busca registros por nome (parcial) e período.
    """
    with get_db_connection() as conn:
        base_query = "SELECT * FROM registros WHERE nome LIKE ?"
        params = [f"%{nome}%"]

        if periodo == "semanal":
            base_query += " AND entrada >= datetime('now', '-7 days')"
        elif periodo == "mensal":
            base_query += " AND entrada >= datetime('now', '-30 days')"

        base_query += " ORDER BY entrada DESC"
        return conn.execute(base_query, params).fetchall()