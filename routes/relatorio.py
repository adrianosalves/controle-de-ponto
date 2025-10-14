# routes/relatorio.py
from fasthtml.common import *
from db.database import buscar_registros_por_colaborador
from utils.calculos import somar_horas_por_registros, formatar_relatorio_horas
from utils.formatacao import formatar_data_brasil

SITUACOES_VALIDAS = ["Trabalho", "Descanso", "Folga Remunerada", "Feriado", "Férias"]
ICONE_SITUACAO = {
    "Trabalho": "🟢",
    "Descanso": "🔵",
    "Folga Remunerada": "🟡",
    "Feriado": "🟣",
    "Férias": "🟠"
}

def get_relatorio_page(nome="", periodo="todos"):
    registros = []
    totais = None
    mensagem = ""

    if nome.strip():
        registros = buscar_registros_por_colaborador(nome.strip(), periodo)
        if registros:
            registros_trabalho = [r for r in registros if (r['situacao_dia'] or "Trabalho") == "Trabalho"]
            totais = somar_horas_por_registros(registros_trabalho)
        else:
            mensagem = "Nenhum registro encontrado."

    formulario = Form(
        Input(name="nome", placeholder="Nome do colaborador", value=nome, required=True, style="padding:8px; width:250px; margin-right:10px;"),
        Select(
            Option("Todos os períodos", value="todos", selected=periodo == "todos"),
            Option("Últimos 7 dias", value="semanal", selected=periodo == "semanal"),
            Option("Últimos 30 dias", value="mensal", selected=periodo == "mensal"),
            name="periodo",
            style="padding:8px; margin-right:10px;"
        ),
        Button("🔍 Gerar Relatório", type="submit", style="padding:8px 16px; background:#4CAF50; color:white; border:none; border-radius:4px; cursor:pointer;"),
        method="get",
        action="/relatorio",
        style="display:flex; gap:10px; margin:20px 0; flex-wrap:wrap; align-items:center;"
    )

    if totais:
        totais_html = Div(
            H3(f"📊 Relatório para: {nome}"),
            P(f"✅ Horas trabalhadas (apenas em dias 'Trabalho'): {totais['total_horas']}h"),
            P(f"🕒 Extras 50%: {totais['extras_50']}h"),
            P(f"🔥 Extras 100% (fim de semana): {totais['extras_100']}h"),
            P(f"🌙 Noturnas (21h-24h): {totais['noturnas']}h"),
            P(f"🌌 Adicional Noturno (0h-7h): {totais['adicional_noturno']}h"),
            P(f"⏱️ Total de intervalos: {totais['intervalo_total']}h"),
            P(f"⏳ Horas pendentes (abaixo de 8h): {totais['horas_pendentes']}h"),style="background:#f0f8ff; padding:15px; border-radius:8px; margin:20px 0; border-left:4px solid #2196F3;"
        )
    else:
        totais_html = Div()

    linhas = []
    for r in registros:
        situacao = r['situacao_dia'] or "Trabalho"
        icone = ICONE_SITUACAO.get(situacao, "⚪")
        status_label = f"{icone} {situacao}"
        status_registro = "✅" if r['saida'] else "⚠️ Pendente"
        
        rel = formatar_relatorio_horas(
            r['entrada'], r['saida'],
            r['inicio_intervalo'], r['fim_intervalo']
        )

        linhas.append(Tr(
            Td(status_registro),
            Td(status_label),
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

    # Número total de colunas: 16
    tabela = Table(
        Thead(Tr(
            Th("Status"),
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
        Tbody(*linhas) if linhas else Tbody(Tr(Td(mensagem or "Preencha o formulário", colspan=16, style="text-align:center; color:#888;")))
    ) if nome else None

    return Main(
        H1("📄 Relatório por Colaborador"),
        formulario,
        totais_html,
        Br(),
        tabela if tabela else None,
        A("← Voltar para o painel", href="/", style="display:inline-block; margin-top:20px; padding:8px 16px; background:#9e9e9e; color:white; text-decoration:none; border-radius:4px;"),
        style="max-width: 1600px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 0.9em;"
    )