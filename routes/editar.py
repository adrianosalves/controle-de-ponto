# routes/editar.py
from fasthtml.common import *
from db.database import get_db_connection
from routes.ponto import SITUACOES_VALIDAS
from datetime import datetime

def get_registro_por_id(registro_id: int):
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT * FROM registros WHERE id = ?", (registro_id,)
        ).fetchone()

def dt_to_input(dt_str):
    return dt_str[:16].replace(" ", "T") if dt_str else ""

def input_to_dt(input_str):
    return datetime.strptime(input_str.replace("T", " ") + ":00", "%Y-%m-%d %H:%M:%S") if input_str else None

def atualizar_registro(registro_id: int, nome: str, entrada: str, saida: str = "", 
                      inicio_intervalo: str = "", fim_intervalo: str = "",
                      situacao_dia: str = "Trabalho", observacoes: str = ""):
    try:
        # Converter para datetime para validação
        dt_entrada = input_to_dt(entrada)
        dt_saida = input_to_dt(saida)
        dt_inicio_int = input_to_dt(inicio_intervalo)
        dt_fim_int = input_to_dt(fim_intervalo)

        # Validação lógica de ordem cronológica
        if dt_saida:
            if dt_saida <= dt_entrada:
                raise ValueError("Saída deve ser após a entrada.")
            if dt_inicio_int and dt_fim_int:
                if not (dt_entrada <= dt_inicio_int < dt_fim_int <= dt_saida):
                    raise ValueError("Intervalo deve estar entre entrada e saída, e início antes do fim.")
            elif dt_inicio_int or dt_fim_int:
                raise ValueError("Informe ambos: Início e Fim do Intervalo.")

        # Formatar para salvar
        entrada_fmt = entrada.replace("T", " ") + ":00"
        saida_fmt = saida.replace("T", " ") + ":00" if saida else None
        inicio_fmt = inicio_intervalo.replace("T", " ") + ":00" if inicio_intervalo else None
        fim_fmt = fim_intervalo.replace("T", " ") + ":00" if fim_intervalo else None

        with get_db_connection() as conn:
            conn.execute("""
                UPDATE registros 
                SET nome = ?, entrada = ?, saida = ?, 
                    inicio_intervalo = ?, fim_intervalo = ?,
                    situacao_dia = ?, observacoes = ?
                WHERE id = ?
            """, (nome.strip(), entrada_fmt, saida_fmt, inicio_fmt, fim_fmt, situacao_dia, observacoes or "", registro_id))
        return True, ""
    except Exception as e:
        return False, str(e)

def get_formulario_edicao(registro_id: int, erro: str = ""):
    registro = get_registro_por_id(registro_id)
    if not registro:
        return Div("Registro não encontrado.", style="color:red; padding:20px; font-size:1.2em;")

    entrada_input = dt_to_input(registro['entrada'])
    saida_input = dt_to_input(registro['saida'])
    inicio_int_input = dt_to_input(registro['inicio_intervalo'])
    fim_int_input = dt_to_input(registro['fim_intervalo'])

    opcoes_situacao = [
        Option(s, value=s, selected=(registro['situacao_dia'] or "Trabalho") == s)
        for s in SITUACOES_VALIDAS
    ]

    erro_html = Div(erro, style="color:red; background:#ffebee; padding:10px; border-radius:4px; margin-bottom:15px;") if erro else ""

    return Main(
        H1(f"✏️ Editar Registro #{registro_id}"),
        P("Preencha os horários na ordem cronológica. O intervalo deve estar entre entrada e saída.", style="color:#555;"),
        erro_html,
        Form(
            Label("Nome:", style="font-weight:bold; display:block; margin-top:15px;"),
            Input(name="nome", value=registro['nome'], required=True, style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Entrada:", style="font-weight:bold; display:block; margin-top:20px; color:#1976D2;"),
            Input(name="entrada", type="datetime-local", value=entrada_input, required=True, style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Início do Intervalo (opcional):", style="font-weight:bold; display:block; margin-top:20px; color:#1976D2;"),
            Input(name="inicio_intervalo", type="datetime-local", value=inicio_int_input, style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Fim do Intervalo (opcional):", style="font-weight:bold; display:block; margin-top:10px; color:#1976D2;"),
            Input(name="fim_intervalo", type="datetime-local", value=fim_int_input, style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Saída:", style="font-weight:bold; display:block; margin-top:20px; color:#d32f2f;"),
            Input(name="saida", type="datetime-local", value=saida_input, style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Situação do Dia:", style="font-weight:bold; display:block; margin-top:20px;"),
            Select(*opcoes_situacao, name="situacao_dia", style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Label("Observações:", style="font-weight:bold; display:block; margin-top:20px;"),
            Input(name="observacoes", value=registro['observacoes'] or "", style="width:100%; padding:10px; margin:5px 0; border:1px solid #ccc; border-radius:4px;"),

            Button("💾 Salvar Alterações", type="submit", style="margin-top:25px; padding:12px 24px; background:#4CAF50; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;"),
            method="post",
            action=f"/atualizar/{registro_id}",
            style="max-width:700px; background:#fff; padding:25px; border-radius:10px; margin:20px auto; box-shadow:0 2px 10px rgba(0,0,0,0.1);"
        ),
        Div(
            A("← Cancelar e voltar", href="/", style="text-decoration:none; padding:10px 20px; background:#f5f5f5; color:#333; border-radius:6px; display:inline-block; margin-top:10px;"),
            style="text-align:center;"
        ),
        style="max-width:800px; margin:0 auto; padding:20px; font-family:sans-serif;"
    )