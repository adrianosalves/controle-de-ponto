# app.py (atualizado)
from fasthtml.common import *
from routes.home import get_home_page
from routes.ponto import registrar_entrada, registrar_saida
from routes.relatorio import get_relatorio_page  # <-- nova importação
from routes.editar import get_formulario_edicao, atualizar_registro


app, rt = fast_app()

@rt("/")
def get():
    return Title("Controle de Ponto"), get_home_page()

# app.py (trecho atualizado)

@rt("/entrada")
def post(nome: str, entrada: str, situacao_dia: str = "Trabalho", observacoes: str = ""):
    registrar_entrada(nome, entrada, situacao_dia, observacoes)
    return RedirectResponse("/", status_code=303)

@rt("/saida")
def post(registro_id: int, saida: str):
    registrar_saida(registro_id, saida)
    return RedirectResponse("/", status_code=303)

# Nova rota de relatório
@rt("/relatorio")
def get(nome: str = "", periodo: str = "todos"):
    return Title("Relatório por Colaborador"), get_relatorio_page(nome, periodo)


# Nova rota: formulário de edição
@rt("/editar/{registro_id}")
def get(registro_id: int):
    return Title("Editar Registro"), get_formulario_edicao(registro_id)

# Nova rota: salvar edição
@rt("/editar/{registro_id}")
def get(registro_id: int):
    return Title("Editar Registro"), get_formulario_edicao(registro_id)

# app.py (atualize a rota de atualização)

@rt("/atualizar/{registro_id}")
def post(registro_id: int, nome: str, entrada: str, saida: str = "", 
         inicio_intervalo: str = "", fim_intervalo: str = "",
         situacao_dia: str = "Trabalho", observacoes: str = ""):
    sucesso, erro = atualizar_registro(registro_id, nome, entrada, saida, inicio_intervalo, fim_intervalo, situacao_dia, observacoes)
    if sucesso:
        return RedirectResponse("/", status_code=303)
    else:
        # Recarrega o formulário com mensagem de erro
        return Title("Editar Registro"), get_formulario_edicao(registro_id, erro=erro)