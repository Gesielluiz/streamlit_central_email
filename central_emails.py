from banco import (
    carregar_configuracao, salvar_configuracao,
    salvar_template, listar_templates, remover_template, carregar_template,
    salvar_lista, listar_listas, remover_lista, carregar_lista
)

from pathlib import Path
import streamlit as st
from utilidades import *

# Diretórios base
PASTA_ATUAL = Path(__file__).parent
PASTA_TEMPLATES = PASTA_ATUAL / 'templates'
PASTA_LISTA_EMAILS = PASTA_ATUAL / 'lista_emails'
PASTA_CONFIGURACOES = PASTA_ATUAL / 'configuracoes'



# Inicializa a página padrão
def inicializacao():
    if 'pagina_central_email' not in st.session_state:
        st.session_state.pagina_central_email = 'home'
    if 'destinatarios_atual' not in st.session_state:
        st.session_state.destinatarios_atual = ''
    if 'titulo_atual' not in st.session_state:
        st.session_state.titulo_atual = ''
    if 'corpo_atual' not in st.session_state:
        st.session_state.corpo_atual = ''



# ================= HOME =================
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
                                args=(destinatarios, titulo, corpo, anexos))
    col3.button('Limpar', use_container_width=True, on_click=_limpar)

    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo

# Anexos
anexos = st.file_uploader(
    "Anexar arquivos (PDF, Word, Excel, etc.)",
    type=["pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"],
    accept_multiple_files=True
)




# Limpa os campos atuais
def _limpar():
    st.session_state.destinatarios_atual = ''
    st.session_state.titulo_atual = ''
    st.session_state.corpo_atual = ''


def _enviar_email(destinatarios, titulo, corpo, anexos=None):
    destinatarios = destinatarios.replace(' ', '').split(',')
    email_usuario = _le_email_usuario()
    chave = _le_chave_usuario()

    if email_usuario == '':
        st.error('Adicione email na página de configurações')
    elif chave == '':
        st.error('Adicione a chave de email na página de configurações')
    else:
        arquivos = []
        if anexos:
            for arquivo in anexos:
                arquivos.append((arquivo.name, arquivo.read()))

        envia_email(
            email_usuario,
            destinatarios=destinatarios,
            titulo=titulo,
            corpo=corpo,
            senha_app=chave,
            anexos=arquivos
        )


        

# ================ TEMPLATE ================
def pag_templates():
    st.markdown('# Templates')
    st.divider()

    for arquivo in PASTA_TEMPLATES.glob('*.txt'):
        nome_arquivo = arquivo.stem.replace('_', ' ').upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_arquivo,
            key=f'{nome_arquivo}',
            use_container_width=True,
            on_click=_usar_template,
            args=(nome_arquivo,)
        )
        col2.button(
            'EDITAR',
            key=f'editar_{nome_arquivo}',
            use_container_width=True,
            on_click=_editar_arquivo,
            args=(nome_arquivo,)
        )
        col3.button(
            'REMOVER',
            key=f'remover_{nome_arquivo}',
            use_container_width=True,
            on_click=_remove_template,
            args=(nome_arquivo,)
        )

    st.divider()
    st.button(
        'Adicionar Template',
        on_click=mudar_pagina,
        args=('adicionar_novo_template',)
    )


def pag_adicionar_novo_template(nome_template='', texto_template=''):
    nome_template = st.text_input(
        'Nome do template',
        value=nome_template
    )
    texto_template = st.text_area(
        'Escreva o texto do template',
        value=texto_template,
        height=600
    )
    st.button(
        'Salvar',
        on_click=_salvar_template,
        args=(nome_template, texto_template)
    )


def _usar_template(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_TEMPLATES / nome_arquivo) as f:
        texto_arquivo = f.read()
    st.session_state.corpo_atual = texto_arquivo
    mudar_pagina('home')


def _salvar_template(nome, texto):
    PASTA_TEMPLATES.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_TEMPLATES / nome_arquivo, 'w') as f:
        f.write(texto)
    mudar_pagina('templates')


def _remove_template(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    caminho = PASTA_TEMPLATES / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina('templates')


def _editar_arquivo(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_TEMPLATES / nome_arquivo) as f:
        texto_arquivo = f.read()
    st.session_state.nome_template_editar = nome
    st.session_state.texto_template_editar = texto_arquivo
    mudar_pagina('editar_template')

# ============== LISTAS EMAIL ==============
def pag_lista_email():
    st.markdown('# Lista Email')
    st.divider()

    for arquivo in PASTA_LISTA_EMAILS.glob('*.txt'):
        nome_arquivo = arquivo.stem.replace('_', ' ').upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_arquivo,
            key=f'{nome_arquivo}',
            use_container_width=True,
            on_click=_usa_lista,
            args=(nome_arquivo,)
        )
        col2.button(
            'EDITAR',
            key=f'editar_{nome_arquivo}',
            use_container_width=True,
            on_click=_editar_lista,
            args=(nome_arquivo,)
        )
        col3.button(
            'REMOVER',
            key=f'remover_{nome_arquivo}',
            use_container_width=True,
            on_click=_remove_lista,
            args=(nome_arquivo,)
        )

    st.divider()
    st.button(
        'Adiciona Lista',
        on_click=mudar_pagina,
        args=('adicionar_nova_lista',)
    )


def pag_adicionar_nova_lista(nome_lista='', emails_lista=''):
    nome_lista = st.text_input(
        'Nome da lista:',
        value=nome_lista
    )
    emails_lista = st.text_area(
        'Escreva os emails separados por vírgula:',
        value=emails_lista,
        height=600
    )
    st.button(
        'Salvar',
        on_click=_salvar_lista,
        args=(nome_lista, emails_lista)
    )

def _usa_lista(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_LISTA_EMAILS / nome_arquivo) as f:
        texto_arquivo = f.read()
    st.session_state.destinatarios_atual = texto_arquivo
    mudar_pagina('home')


def _salvar_lista(nome, texto):
    PASTA_LISTA_EMAILS.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_LISTA_EMAILS / nome_arquivo, 'w') as f:
        f.write(texto)
    mudar_pagina('lista_emails')


def _remove_lista(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    caminho = PASTA_LISTA_EMAILS / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina('lista_emails')


def _editar_lista(nome):
    nome_arquivo = nome.replace(' ', '_').lower() + '.txt'
    with open(PASTA_LISTA_EMAILS / nome_arquivo) as f:
        texto_arquivo = f.read()
    st.session_state.nome_lista_editar = nome
    st.session_state.texto_lista_editar = texto_arquivo
    mudar_pagina('editar_lista')

# ============ CONFIGURAÇÕES ============
def pag_configuracao():
    st.markdown('# Configurações')
    email = st.text_input('Digite o seu email:')
    st.button('Salvar', key='salvar_email',
                        on_click=_salvar_email,
                        args=(email, ))
    
    chave = st.text_input('Digite a chave de email:')
    st.button('Salvar chave', key='salvar_chave',
                        on_click=_salvar_chave,
                        args=(chave, ))

def _salvar_email(email):
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    with open(PASTA_CONFIGURACOES / 'email_usuario.txt', 'w') as f:
        f.write(email)

def _salvar_chave(chave):
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    with open(PASTA_CONFIGURACOES / 'chave.txt', 'w') as f:
        f.write(chave)

def _le_email_usuario():
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    if (PASTA_CONFIGURACOES / 'email_usuario.txt').exists():
        with open(PASTA_CONFIGURACOES / 'email_usuario.txt', 'r') as f:
            return f.read()
    return ''

def _le_chave_usuario():
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    if (PASTA_CONFIGURACOES / 'chave.txt').exists():
        with open(PASTA_CONFIGURACOES / 'chave.txt', 'r') as f:
            return f.read()
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



