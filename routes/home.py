# routes/home.py
from fasthtml.common import *
from db.database import get_db_connection
from utils.calculos import formatar_relatorio_horas, somar_horas_por_registros
from utils.formatacao import formatar_data_brasil

SITUACOES_VALIDAS = ["Trabalho", "Descanso", "Folga Remunerada", "Feriado", "Férias"]

def get_home_page():
    with get_db_connection() as conn:
        # Registros recentes (todos)
        registros = conn.execute(
            "SELECT * FROM registros ORDER BY entrada DESC"
        ).fetchall()
        
        # Só registros de "Trabalho" para cálculo de pendência
        registros_trabalho = conn.execute(
            "SELECT * FROM registros WHERE situacao_dia = 'Trabalho'"
        ).fetchall()

    # Calcula resumo de horas pendentes
    resumo = somar_horas_por_registros(registros_trabalho)
    resumo_html = Div(
        P(
            f"⏳ Horas pendentes (abaixo de 8h): {resumo['horas_pendentes']}h",
            style="background:#fff8e1; padding:10px; border-radius:6px; font-weight:bold; color:#e65100; display:inline-block;"
        ),
        style="text-align:right; margin: 15px 0;"
    )

    icone_situacao = {
        "Trabalho": "🟢",
        "Descanso": "🔵",
        "Folga Remunerada": "🟡",
        "Feriado": "🟣",
        "Férias": "🟠"
    }

    linhas = []
    for r in registros:
        situacao = r['situacao_dia'] or "Trabalho"
        icone = icone_situacao.get(situacao, "⚪")
        rel = formatar_relatorio_horas(
            r['entrada'], r['saida'],
            r['inicio_intervalo'], r['fim_intervalo']
        )
        linhas.append(Tr(
            Td(f"{icone} {situacao}"),
            Td(A("✏️ Editar", href=f"/editar/{r['id']}", style="text-decoration:none; color:#1976D2;")),
            Td(r['id']),
            Td(r['nome']),
            Td(formatar_data_brasil(r['entrada'], incluir_hora=True)),
            Td(formatar_data_brasil(r['inicio_intervalo'], incluir_hora=True)),
            Td(formatar_data_brasil(r['fim_intervalo'], incluir_hora=True)),
            Td(formatar_data_brasil(r['saida'], incluir_hora=True)),
            Td(rel["total"]),
            Td(rel["extras_50"]),
            Td(rel["extras_100"]),
            Td(rel["noturnas"]),
            Td(rel["adicional_noturno"]),
            Td(rel["intervalo"]),
            Td(r['observacoes'] or "—")
        ))

    opcoes_situacao = [Option(s, value=s) for s in SITUACOES_VALIDAS]

    return Main(
        H1("📊 Controle de Horários dos Colaboradores"),
        P(
            A("📄 Ver relatório detalhado por colaborador", href="/relatorio"),
            style="margin-bottom: 20px; display: inline-block;"
        ),
        
        Section(
            H2("Registrar Entrada"),
            Form(
                Label("Nome do colaborador:", style="font-weight:bold;"),
                Input(name="nome", placeholder="Ex: João Silva", required=True, style="width:100%; margin:5px 0; padding:8px;"),
                
                Label("Data e hora de entrada:", style="font-weight:bold; margin-top:10px;"),
                Input(name="entrada", type="datetime-local", required=True, style="width:100%; margin:5px 0; padding:8px;"),
                
                Label("Situação do Dia:", style="font-weight:bold; margin-top:10px;"),
                Select(*opcoes_situacao, name="situacao_dia", style="width:100%; margin:5px 0; padding:8px;"),
                
                Label("Observações (opcional):", style="font-weight:bold; margin-top:10px;"),
                Input(name="observacoes", placeholder="Ex: Atendimento externo...", style="width:100%; margin:5px 0; padding:8px;"),
                
                Button("✅ Registrar Entrada", type="submit", style="margin-top:15px; padding:10px 20px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;"),
                method="post",
                action="/entrada",
                style="max-width:600px; background:#f9f9f9; padding:20px; border-radius:8px; margin:20px 0;"
            )
        ),

        Br(),
        resumo_html,  # ✅ Exibe o resumo de horas pendentes aqui
        H2("Registros Recentes"),
        Table(
            Thead(Tr(
                Th("Situação do Dia"),
                Th("Ações"),
                Th("ID"),
                Th("Nome"),
                Th("Entrada"),
                Th("Início Intervalo"),
                Th("Fim Intervalo"),
                Th("Saída"),
                Th("Total"),
                Th("50%"),
                Th("100%"),
                Th("Noturnas"),
                Th("Adic. Noturno"),
                Th("Intervalo"),
                Th("Observações")
            )),
            Tbody(*linhas) if linhas else Tbody(Tr(Td("Nenhum registro encontrado", colspan=15, style="text-align:center; color:#888;")))
        ),
        style="max-width: 1600px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 0.9em;"
    )