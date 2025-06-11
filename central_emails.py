# central_emails.py

import os, streamlit as st

st.write("DATABASE_URL =", os.getenv("DATABASE_URL"))


from pathlib import Path
import os
import uuid
import streamlit as st

# Importa tudo do banco (já com salvar_email_enviado e listar_rastreamentos)
from banco import (
    carregar_configuracao,
    salvar_configuracao,
    salvar_template,
    listar_templates,
    remover_template,
    carregar_template,
    salvar_lista,
    listar_listas,
    remover_lista,
    carregar_lista,
    salvar_email_enviado,
    listar_rastreamentos,
)

from utilidades import mudar_pagina, envia_email, _le_email_usuario, _le_chave_usuario

# Diretórios base (para arquivos locais de template / lista)
PASTA_ATUAL = Path(__file__).parent
PASTA_TEMPLATES = PASTA_ATUAL / "templates"
PASTA_LISTA_EMAILS = PASTA_ATUAL / "lista_emails"
PASTA_CONFIGURACOES = PASTA_ATUAL / "configuracoes"


# ===========================================
#  Funções de Inicialização e Limpeza (HOME)
# ===========================================
def inicializacao():
    if "pagina_central_email" not in st.session_state:
        st.session_state.pagina_central_email = "home"
    if "destinatarios_atual" not in st.session_state:
        st.session_state.destinatarios_atual = ""
    if "titulo_atual" not in st.session_state:
        st.session_state.titulo_atual = ""
    if "corpo_atual" not in st.session_state:
        st.session_state.corpo_atual = ""


def _limpar():
    st.session_state.destinatarios_atual = ""
    st.session_state.titulo_atual = ""
    st.session_state.corpo_atual = ""


# =========================
#  PÁGINA: HOME (Envio)
# =========================
def home():
    # Carrega estados anteriores (ou vazios)
    destinatarios_atual = st.session_state.destinatarios_atual
    titulo_atual = st.session_state.titulo_atual
    corpo_atual = st.session_state.corpo_atual

    st.markdown("# Central de Emails")
    destinatarios = st.text_input("Destinatários do email:", value=destinatarios_atual)
    titulo = st.text_input("Título do email:", value=titulo_atual)
    corpo = st.text_area("Digite o email:", value=corpo_atual, height=300)

    # Upload de anexos (opcional)
    anexos = st.file_uploader(
        "Anexar arquivos (PDF, Word, Excel, etc.)",
        type=["pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"],
        accept_multiple_files=True,
    )

    col1, col2 = st.columns([0.5, 0.5])
    col1.button(
        "Enviar email",
        use_container_width=True,
        on_click=_enviar_email,
        args=(destinatarios, titulo, corpo, anexos),
    )
    col2.button("Limpar", use_container_width=True, on_click=_limpar)

    # Armazena no state (para reaproveitar)
    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo


def _enviar_email(destinatarios, titulo, corpo, anexos=None):
    # 1) Converte string em lista
    destinatarios = destinatarios.replace(" ", "").split(",")

    # 2) Lê e-mail e chave
    email_usuario = _le_email_usuario()
    chave = _le_chave_usuario()
    if not email_usuario or not chave:
        st.error("Configurações faltando")
        return

    # 3) Gera rastreio_id
    rastreio_id = str(uuid.uuid4())

    # 4) Monta URL do pixel usando FLASK_BASE_URL
    host_pixel = os.getenv("FLASK_BASE_URL") or "http://localhost:5000"
    pixel_url = f"{host_pixel}/rastreamento?id={rastreio_id}"

    # 5) Constrói o corpo HTML com pixel
    corpo_html = (
        corpo.replace("\n", "<br>")
        + f'<br><br><img src="{pixel_url}" width="1" height="1" style="display:none;" />'
    )

    # 6) Grava no DB
    for d in destinatarios:
        salvar_email_enviado(d, titulo, corpo_html, rastreio_id)

    # 7) Prepara anexos
    arquivos = []
    if anexos:
        for arquivo in anexos:
            arquivos.append((arquivo.name, arquivo.read()))

    # 8) Envia o e-mail
    envia_email(
        email_usuario=email_usuario,
        destinatarios=destinatarios,
        titulo=titulo,
        corpo=corpo_html,
        senha_app=chave,
        anexos=arquivos,
    )


# ================================
#  PÁGINA: TEMPLATES
# ================================
def pag_templates():
    st.markdown("# Templates")
    st.divider()

    for arquivo in PASTA_TEMPLATES.glob("*.txt"):
        nome_arquivo = arquivo.stem.replace("_", " ").upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_arquivo,
            key=f"{nome_arquivo}",
            use_container_width=True,
            on_click=_usar_template,
            args=(nome_arquivo,),
        )
        col2.button(
            "EDITAR",
            key=f"editar_{nome_arquivo}",
            use_container_width=True,
            on_click=_editar_arquivo,
            args=(nome_arquivo,),
        )
        col3.button(
            "REMOVER",
            key=f"remover_{nome_arquivo}",
            use_container_width=True,
            on_click=_remove_template,
            args=(nome_arquivo,),
        )

    st.divider()
    st.button("Adicionar Template", on_click=mudar_pagina, args=("adicionar_novo_template",))


def pag_adicionar_novo_template(nome_template="", texto_template=""):
    nome_template = st.text_input("Nome do template", value=nome_template)
    texto_template = st.text_area("Escreva o texto do template", value=texto_template, height=400)
    st.button("Salvar", on_click=_salvar_template, args=(nome_template, texto_template))


def _usar_template(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_TEMPLATES / nome_arquivo) as f:
        texto_arquivo = f.read()
    st.session_state.corpo_atual = texto_arquivo
    mudar_pagina("home")


def _salvar_template(nome, texto):
    PASTA_TEMPLATES.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_TEMPLATES / nome_arquivo, "w", encoding="utf-8") as f:
        f.write(texto)
    mudar_pagina("templates")


def _remove_template(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_TEMPLATES / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina("templates")


def _editar_arquivo(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_TEMPLATES / nome_arquivo, "r", encoding="utf-8") as f:
        texto_arquivo = f.read()
    st.session_state.nome_template_editar = nome
    st.session_state.texto_template_editar = texto_arquivo
    mudar_pagina("editar_template")


# ===============================
#  PÁGINA: LISTA DE EMAILS
# ===============================
def pag_lista_email():
    st.markdown("# Lista Email")
    st.divider()

    for arquivo in PASTA_LISTA_EMAILS.glob("*.txt"):
        nome_arquivo = arquivo.stem.replace("_", " ").upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_arquivo,
            key=f"{nome_arquivo}",
            use_container_width=True,
            on_click=_usa_lista,
            args=(nome_arquivo,),
        )
        col2.button(
            "EDITAR",
            key=f"editar_{nome_arquivo}",
            use_container_width=True,
            on_click=_editar_lista,
            args=(nome_arquivo,),
        )
        col3.button(
            "REMOVER",
            key=f"remover_{nome_arquivo}",
            use_container_width=True,
            on_click=_remove_lista,
            args=(nome_arquivo,),
        )

    st.divider()
    st.button("Adiciona Lista", on_click=mudar_pagina, args=("adicionar_nova_lista",))


def pag_adicionar_nova_lista(nome_lista="", emails_lista=""):
    nome_lista = st.text_input("Nome da lista:", value=nome_lista)
    emails_lista = st.text_area("Escreva os emails separados por vírgula:", value=emails_lista, height=400)
    st.button("Salvar", on_click=_salvar_lista, args=(nome_lista, emails_lista))


def _usa_lista(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_LISTA_EMAILS / nome_arquivo, "r", encoding="utf-8") as f:
        texto_arquivo = f.read()
    st.session_state.destinatarios_atual = texto_arquivo
    mudar_pagina("home")


def _salvar_lista(nome, texto):
    PASTA_LISTA_EMAILS.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_LISTA_EMAILS / nome_arquivo, "w", encoding="utf-8") as f:
        f.write(texto)
    mudar_pagina("lista_emails")


def _remove_lista(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_LISTA_EMAILS / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina("lista_emails")


def _editar_lista(nome):
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_LISTA_EMAILS / nome_arquivo, "r", encoding="utf-8") as f:
        texto_arquivo = f.read()
    st.session_state.nome_lista_editar = nome
    st.session_state.texto_lista_editar = texto_arquivo
    mudar_pagina("editar_lista")


# =====================================
#  PÁGINA: CONFIGURAÇÃO (Leitura/Grava)
# =====================================
def pag_configuracao():
    st.markdown("# Configurações")
    dados = carregar_configuracao()
    email = st.text_input("Digite o seu email:", value=dados["email_usuario"])
    chave = st.text_input("Digite a chave de email:", value=dados["chave_email"])
    st.button("Salvar", key="btn_salvar_conf", on_click=_btn_salvar_conf, args=(email, chave))

def _btn_salvar_conf(email, chave):
    salvar_configuracao(email, chave)
    st.success("Configuração salva!")


# ========= PÁGINA: RASTREAMENTO =========


def pag_rastreamento():
    st.markdown("# Rastreamento de Abertura")
    st.divider()
    # Busca todos os eventos já salvos no banco
    eventos = listar_rastreamentos()
    if eventos:
        # Exibe numa tabela interativa
        st.dataframe(eventos)
    else:
        st.info("Ainda não há eventos de rastreamento cadastrados.")



# ================ MAIN ==================
def main():
    inicializacao()

    # Sidebar (menu principal)
    st.sidebar.button(
        "Central de Emails", use_container_width=True, on_click=mudar_pagina, args=("home",)
    )
    st.sidebar.button(
        "Templates", use_container_width=True, on_click=mudar_pagina, args=("templates",)
    )
    st.sidebar.button(
        "Lista de Emails", use_container_width=True, on_click=mudar_pagina, args=("lista_emails",)
    )
    st.sidebar.button(
        "Configuração", use_container_width=True, on_click=mudar_pagina, args=("configuracao",)
    )
    st.sidebar.button(
        "Rastreamento", use_container_width=True, on_click=mudar_pagina, args=("rastreamento",)
    )

    # Roteamento de páginas
    pagina = st.session_state.pagina_central_email
    if pagina == "home":
        home()
    elif pagina == "templates":
        pag_templates()
    elif pagina == "adicionar_novo_template":
        nome_ed = st.session_state.get("nome_template_editar", "")
        texto_ed = st.session_state.get("texto_template_editar", "")
        pag_adicionar_novo_template(nome_ed, texto_ed)
    elif pagina == "lista_emails":
        pag_lista_email()
    elif pagina == "adicionar_nova_lista":
        pag_adicionar_nova_lista()
    elif pagina == "editar_lista":
        nome_li = st.session_state.get("nome_lista_editar", "")
        texto_li = st.session_state.get("texto_lista_editar", "")
        pag_adicionar_nova_lista(nome_li, texto_li)
    elif pagina == "configuracao":
        pag_configuracao()
    elif pagina == "rastreamento":
        pag_rastreamento()

if __name__ == "__main__":
    main()
