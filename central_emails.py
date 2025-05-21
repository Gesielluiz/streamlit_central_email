from pathlib import Path
import streamlit as st
from utilidades import *
from banco import (
    carregar_configuracao, salvar_configuracao,
    salvar_template, listar_templates, remover_template, carregar_template,
    salvar_lista, listar_listas, remover_lista, carregar_lista
)

def inicializacao():
    if 'pagina_central_email' not in st.session_state:
        st.session_state.pagina_central_email = 'home'
    if 'destinatarios_atual' not in st.session_state:
        st.session_state.destinatarios_atual = ''
    if 'titulo_atual' not in st.session_state:
        st.session_state.titulo_atual = ''
    if 'corpo_atual' not in st.session_state:
        st.session_state.corpo_atual = ''

def home():
    destinatarios_atual = st.session_state.destinatarios_atual
    titulo_atual = st.session_state.titulo_atual
    corpo_atual = st.session_state.corpo_atual

    st.markdown('# Central de Emails')
    destinatarios = st.text_input('Destinatários do email:', value=destinatarios_atual)
    titulo = st.text_input('Título do email:', value=titulo_atual)
    corpo = st.text_area('Digite o email:', value=corpo_atual, height=400)
    col1, col2, col3 = st.columns(3)
    col1.button('Enviar email', use_container_width=True,
                on_click=_enviar_email,
                args=(destinatarios, titulo, corpo))
    col3.button('Limpar', use_container_width=True, on_click=_limpar)

    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo

def _limpar():
    st.session_state.destinatarios_atual = ''
    st.session_state.titulo_atual = ''
    st.session_state.corpo_atual = ''

def _enviar_email(destinatarios, titulo, corpo):
    destinatarios = destinatarios.replace(' ', '').split(',')
    dados = carregar_configuracao()
    email_usuario = dados["email_usuario"]
    chave = dados["chave_email"]
    if email_usuario == '':
        st.error('Adicione email na página de configurações')
    elif chave == '':
        st.error('Adicione a chave de email na página de configurações')
    else:
        envia_email(email_usuario,
                    destinatarios=destinatarios,
                    titulo=titulo,
                    corpo=corpo,
                    senha_app=chave)

# ========== Templates ==========
def pag_templates():
    st.markdown('# Templates')
    st.divider()

    for template in listar_templates():
        nome_template = template["nome_template"]
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_template.upper(),
            key=f'{nome_template}',
            use_container_width=True,
            on_click=_usar_template,
            args=(nome_template,)
        )
        col2.button(
            'EDITAR',
            key=f'editar_{nome_template}',
            use_container_width=True,
            on_click=_editar_arquivo,
            args=(nome_template,)
        )
        col3.button(
            'REMOVER',
            key=f'remover_{nome_template}',
            use_container_width=True,
            on_click=_remove_template,
            args=(nome_template,)
        )

    st.divider()
    st.button(
        'Adicionar Template',
        on_click=mudar_pagina,
        args=('adicionar_novo_template',)
    )

def pag_adicionar_novo_template(nome_template='', texto_template=''):
    nome_template = st.text_input('Nome do template', value=nome_template)
    texto_template = st.text_area('Escreva o texto do template', value=texto_template, height=600)
    st.button('Salvar', on_click=lambda: salvar_template(nome_template, texto_template))

def _usar_template(nome):
    texto = carregar_template(nome)
    st.session_state.corpo_atual = texto
    mudar_pagina('home')

def _remove_template(nome):
    remover_template(nome)
    mudar_pagina('templates')

def _editar_arquivo(nome):
    texto = carregar_template(nome)
    st.session_state.nome_template_editar = nome
    st.session_state.texto_template_editar = texto
    mudar_pagina('editar_template')

# ========== Lista de Emails ==========
def pag_lista_email():
    st.markdown('# Lista Email')
    st.divider()

    for lista in listar_listas():
        nome_lista = lista["nome_lista"]
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_lista.upper(),
            key=f'{nome_lista}',
            use_container_width=True,
            on_click=_usa_lista,
            args=(nome_lista,)
        )
        col2.button(
            'EDITAR',
            key=f'editar_{nome_lista}',
            use_container_width=True,
            on_click=_editar_lista,
            args=(nome_lista,)
        )
        col3.button(
            'REMOVER',
            key=f'remover_{nome_lista}',
            use_container_width=True,
            on_click=_remove_lista,
            args=(nome_lista,)
        )

    st.divider()
    st.button('Adiciona Lista', on_click=mudar_pagina, args=('adicionar_nova_lista',))

def pag_adicionar_nova_lista(nome_lista='', emails_lista=''):
    nome_lista = st.text_input('Nome da lista:', value=nome_lista)
    emails_lista = st.text_area('Escreva os emails separados por vírgula:', value=emails_lista, height=600)
    st.button('Salvar', on_click=lambda: salvar_lista(nome_lista, emails_lista))

def _usa_lista(nome):
    texto = carregar_lista(nome)
    st.session_state.destinatarios_atual = texto
    mudar_pagina('home')

def _remove_lista(nome):
    remover_lista(nome)
    mudar_pagina('lista_emails')

def _editar_lista(nome):
    texto = carregar_lista(nome)
    st.session_state.nome_lista_editar = nome
    st.session_state.texto_lista_editar = texto
    mudar_pagina('editar_lista')

# ========== Configuração ==========
def pag_configuracao():
    st.markdown('# Configurações')
    dados = carregar_configuracao()
    email = st.text_input('Digite o seu email:', value=dados["email_usuario"])
    chave = st.text_input('Digite a chave de email:', value=dados["chave_email"])
    st.button('Salvar', key='salvar_config',
              on_click=lambda: salvar_configuracao(email, chave))

# ========== MAIN ==========
def main():
    inicializacao()

    st.sidebar.button('Central de Emails', use_container_width=True, on_click=mudar_pagina, args=('home',))
    st.sidebar.button('Templates', use_container_width=True, on_click=mudar_pagina, args=('templates',))
    st.sidebar.button('Lista de Emails', use_container_width=True, on_click=mudar_pagina, args=('lista_emails',))
    st.sidebar.button('Configuração', use_container_width=True, on_click=mudar_pagina, args=('configuracao',))

    pagina = st.session_state.pagina_central_email
    if pagina == 'home':
        home()
    elif pagina == 'templates':
        pag_templates()
    elif pagina == 'adicionar_novo_template':
        pag_adicionar_novo_template()
    elif pagina == 'editar_template':
        pag_adicionar_novo_template(st.session_state.nome_template_editar, st.session_state.texto_template_editar)
    elif pagina == 'lista_emails':
        pag_lista_email()
    elif pagina == 'adicionar_nova_lista':
        pag_adicionar_nova_lista()
    elif pagina == 'editar_lista':
        pag_adicionar_nova_lista(st.session_state.nome_lista_editar, st.session_state.texto_lista_editar)
    elif pagina == 'configuracao':
        pag_configuracao()

if __name__ == '__main__':
    main()
