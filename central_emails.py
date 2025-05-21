import streamlit as st
from banco import (
    carregar_configuracao, salvar_configuracao,
    salvar_template, listar_templates, remover_template, carregar_template,
    salvar_lista, listar_listas, remover_lista, carregar_lista
)
from utilidades import envia_email
from pathlib import Path

# Diretórios base (usados apenas para sensores de template/local, mas DB é o principal)
PASTA_ATUAL = Path(__file__).parent
PAGINAS = [
    'home', 'templates', 'adicionar_novo_template', 'lista_emails',
    'adicionar_nova_lista', 'configuracao'
]

def mudar_pagina(nome_pagina):
    st.session_state.pagina = nome_pagina

def inicializacao():
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'home'
    if 'destinatarios_atual' not in st.session_state:
        st.session_state.destinatarios_atual = ''
        st.session_state.titulo_atual = ''
        st.session_state.corpo_atual = ''
    # Para edição de template/lista
    if 'nome_template_editar' not in st.session_state:
        st.session_state.nome_template_editar = ''
        st.session_state.texto_template_editar = ''
    if 'nome_lista_editar' not in st.session_state:
        st.session_state.nome_lista_editar = ''
        st.session_state.texto_lista_editar = ''

# ======== HOME ========
def home():
    st.markdown('# Central de Emails')
    destinatarios = st.text_input('Destinatários:', st.session_state.destinatarios_atual)
    titulo = st.text_input('Título:', st.session_state.titulo_atual)
    corpo = st.text_area('Corpo do email:', st.session_state.corpo_atual, height=300)

    col1, col2 = st.columns(2)
    col1.button('Enviar', use_container_width=True,
                on_click=_enviar_email, args=(destinatarios, titulo, corpo))
    col2.button('Limpar', use_container_width=True, on_click=_limpar)

    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo

def _limpar():
    st.session_state.destinatarios_atual = ''
    st.session_state.titulo_atual = ''
    st.session_state.corpo_atual = ''

def _enviar_email(destinatarios, titulo, corpo):
    dests = [d.strip() for d in destinatarios.split(',') if d.strip()]
    cfg = carregar_configuracao()
    if not cfg['email_usuario'] or not cfg['chave_email']:
        st.error('Configure email e chave antes.')
        return
    envia_email(cfg['email_usuario'], dests, titulo, corpo, senha_app=cfg['chave_email'])
    st.success('Email enviado!')

# ======== TEMPLATES ========
def pag_templates():
    st.markdown('# Templates')
    st.divider()
    for i, tpl in enumerate(listar_templates()):
        nome = tpl['nome_template']
        col1, col2, col3 = st.columns([0.6,0.2,0.2])
        col1.button(nome.upper(), key=f'nome_tpl_{i}', use_container_width=True,
                    on_click=_usar_template, args=(nome,))
        col2.button('EDITAR', key=f'edit_tpl_{i}', use_container_width=True,
                    on_click=_editar_arquivo, args=(nome,))
        col3.button('REMOVER', key=f'rem_tpl_{i}', use_container_width=True,
                    on_click=_remove_template, args=(nome,))
    st.divider()
    st.button('Adicionar Template', key='btn_add_tpl',
              on_click=mudar_pagina, args=('adicionar_novo_template',))

def pag_adicionar_novo_template():
    st.markdown('# Adicionar / Editar Template')
    nome = st.text_input('Nome do template', key='input_nome_tpl',
                        value=st.session_state.nome_template_editar)
    texto = st.text_area('Texto do template', key='input_txt_tpl',
                         value=st.session_state.texto_template_editar, height=400)
    if st.button('Salvar Template', key='btn_salvar_tpl', use_container_width=True):
        salvar_template(nome, texto)
        st.session_state.nome_template_editar = ''
        st.session_state.texto_template_editar = ''
        mudar_pagina('templates')

def _usar_template(nome):
    st.session_state.corpo_atual = carregar_template(nome)
    mudar_pagina('home')

def _remove_template(nome):
    remover_template(nome)
    mudar_pagina('templates')

def _editar_arquivo(nome):
    st.session_state.nome_template_editar = nome
    st.session_state.texto_template_editar = carregar_template(nome)
    mudar_pagina('adicionar_novo_template')

# ======== LISTA DE EMAILS ========
def pag_lista_email():
    st.markdown('# Listas de Email')
    st.divider()
    for i, lst in enumerate(listar_listas()):
        n

