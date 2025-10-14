# routes/ponto.py (atualizado)

from fasthtml.common import *
from db.database import get_db_connection

# Lista de status válidos
SITUACOES_VALIDAS = ["Trabalho", "Descanso", "Folga Remunerada", "Feriado", "Férias"]

def registrar_entrada(nome: str, entrada: str, situacao_dia: str = "Trabalho", observacoes: str = ""):
    nome = nome.strip()
    if not nome:
        return False
    if situacao_dia not in SITUACOES_VALIDAS:
        situacao_dia = "Trabalho"
    entrada_fmt = entrada.replace("T", " ") + ":00"
    with get_db_connection() as conn:
        conn.execute(
            """INSERT INTO registros 
               (nome, entrada, saida, inicio_intervalo, fim_intervalo, situacao_dia, observacoes) 
               VALUES (?, ?, NULL, NULL, NULL, ?, ?)""",
            (nome, entrada_fmt, situacao_dia, observacoes or "")
        )
    return True

def registrar_saida(registro_id: int, saida: str):
    if registro_id <= 0:
        return False
    saida_fmt = saida.replace("T", " ") + ":00"
    with get_db_connection() as conn:
        cur = conn.execute(
            "SELECT id FROM registros WHERE id = ? AND saida IS NULL", 
            (registro_id,)
        )
        if not cur.fetchone():
            return False
        conn.execute(
            "UPDATE registros SET saida = ? WHERE id = ?",
            (saida_fmt, registro_id)
        )
    return True