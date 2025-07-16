from pathlib import Path
import os
import uuid
import streamlit as st

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
)
from utilidades import mudar_pagina, envia_email, _le_email_usuario, _le_chave_usuario

# Diretórios base (para arquivos locais)
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
    destinatarios_atual = st.session_state.destinatarios_atual
    titulo_atual = st.session_state.titulo_atual
    corpo_atual = st.session_state.corpo_atual

    st.markdown("# Central de Emails")
    destinatarios = st.text_input("Destinatários do email:", value=destinatarios_atual)
    titulo = st.text_input("Título do email:", value=titulo_atual)
    corpo = st.text_area("Digite o email:", value=corpo_atual, height=300)

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

    # Armazena no state
    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo


def _enviar_email(destinatarios, titulo, corpo, anexos=None):
    # limpa e quebra
    destinatarios = [d.strip() for d in destinatarios.split(",") if d.strip()]

    email_usuario = _le_email_usuario()
    chave         = _le_chave_usuario()
    if not email_usuario or not chave:
        st.error("Por favor, configure seu e‑mail e chave na página de Configuração")
        return

    # monta lista de arquivos [(nome, bytes), ...]
    arquivos = []
    if anexos:
        for arquivo in anexos:
            arquivos.append((arquivo.name, arquivo.read()))

    # dispara o email, passando mesmo que arquivos = []
    envia_email(
        email_usuario=email_usuario,
        destinatarios=destinatarios,
        titulo=titulo,
        corpo=corpo,
        senha_app=chave,
        anexos=arquivos
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

import streamlit as st
from pathlib import Path

# Caminho da pasta de configuração
PASTA_CONFIGURACOES = Path(__file__).parent / 'configuracoes'


# ============ CONFIGURAÇÕES ============
def pag_configuracao():
    st.markdown('# Configurações')

    # Lê valores salvos
    email_salvo = _le_email_usuario()
    chave_salva = _le_chave_usuario()

    # Campos com valores pré-preenchidos
    email = st.text_input('Digite o seu email:', value=email_salvo or "")
    if st.button('Salvar', key='salvar_email'):
        if email.strip():
            _salvar_email(email)
            st.success('Email salvo com sucesso!')
        else:
            st.warning('Digite um e-mail válido.')

    chave = st.text_input('Digite a chave de email:', value=chave_salva or "", type="password")
    if st.button('Salvar chave', key='salvar_chave'):
        if chave.strip():
            _salvar_chave(chave)
            st.success('Chave salva com sucesso!')
        else:
            st.warning('Digite uma chave válida.')


# ============ FUNÇÕES AUXILIARES ============
def _salvar_email(email):
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    with open(PASTA_CONFIGURACOES / 'email_usuario.txt', 'w', encoding='utf-8') as f:
        f.write(email.strip())

def _salvar_chave(chave):
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    with open(PASTA_CONFIGURACOES / 'chave.txt', 'w', encoding='utf-8') as f:
        f.write(chave.strip())

def _le_email_usuario():
    try:
        with open(PASTA_CONFIGURACOES / 'email_usuario.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''

def _le_chave_usuario():
    try:
        with open(PASTA_CONFIGURACOES / 'chave.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''


# ================ MAIN ==================
def main():
    inicializacao()

    st.sidebar.button(
        'Central de Emails',
        use_container_width=True,
        on_click=mudar_pagina,
        args=('home',)
    )
    st.sidebar.button(
        'Templates',
        use_container_width=True,
        on_click=mudar_pagina,
        args=('templates',)
    )
    st.sidebar.button(
        'Lista de Emails',
        use_container_width=True,
        on_click=mudar_pagina,
        args=('lista_emails',)
    )
    st.sidebar.button(
        'Configuração',
        use_container_width=True,
        on_click=mudar_pagina,
        args=('configuracao',)
    )

    pagina = st.session_state.pagina_central_email
    if pagina == 'home':
        home()
    elif pagina == 'templates':
        pag_templates()
    elif pagina == 'adicionar_novo_template':
        pag_adicionar_novo_template()
    elif pagina == 'editar_template':
        nome_template_editar = st.session_state.nome_template_editar
        texto_template_editar = st.session_state.texto_template_editar
        pag_adicionar_novo_template(nome_template_editar, texto_template_editar)
    elif pagina == 'lista_emails':
        pag_lista_email()
    elif pagina == 'adicionar_nova_lista':
        pag_adicionar_nova_lista()
    elif pagina == 'editar_lista':
        nome_lista = st.session_state.nome_lista_editar
        texto_lista = st.session_state.texto_lista_editar
        pag_adicionar_nova_lista(nome_lista, texto_lista)
    elif pagina == 'configuracao':
        pag_configuracao()

if __name__ == '__main__':
    main()
