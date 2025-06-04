# central_emails.py

from pathlib import Path
import streamlit as st

# Importa funções do módulo 'banco.py' (que você já deve ter criado e configurado)
from banco import (
    carregar_configuracao, salvar_configuracao,
    salvar_template, listar_templates, remover_template, carregar_template,
    salvar_lista, listar_listas, remover_lista, carregar_lista
)

# Importa utilitários (troca de página, envio de e-mail, leitura de credenciais, etc.)
from utilidades import (
    mudar_pagina,
    envia_email,
    _le_email_usuario,
    _le_chave_usuario
)

#
# ============================
#  Definições de pastas
# ============================
#
PASTA_ATUAL = Path(__file__).parent
PASTA_TEMPLATES = PASTA_ATUAL / "templates"
PASTA_LISTA_EMAILS = PASTA_ATUAL / "lista_emails"
PASTA_CONFIGURACOES = PASTA_ATUAL / "configuracoes"


#
# ============================
#  Função de inicialização
# ============================
#
def inicializacao():
    """
    Garante que as chaves de session_state estejam inicializadas
    antes de qualquer coisa (para persistir títulos e corpo ao navegar).
    """
    if "pagina_central_email" not in st.session_state:
        st.session_state.pagina_central_email = "home"
    if "destinatarios_atual" not in st.session_state:
        st.session_state.destinatarios_atual = ""
    if "titulo_atual" not in st.session_state:
        st.session_state.titulo_atual = ""
    if "corpo_atual" not in st.session_state:
        st.session_state.corpo_atual = ""


#
# ============================
#  Página inicial (Home)
# ============================
#
def home():
    """
    Tela principal: campos de destinatários, título, corpo e anexo.
    Os anexos são carregados dinamicamente toda vez que 'home' é renderizado.
    """
    # Primeiro: capturamos anexos diretamente dentro de home()
    anexos = st.file_uploader(
        "Anexar arquivos (PDF, Word, Excel, etc.)",
        type=["pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"],
        accept_multiple_files=True,
    )

    # Recuperamos o que já estava em sessão (para preservar estados entre páginas)
    destinatarios_atual = st.session_state.destinatarios_atual
    titulo_atual = st.session_state.titulo_atual
    corpo_atual = st.session_state.corpo_atual

    st.markdown("# Central de Emails")
    destinatarios = st.text_input("Destinatários do email:", value=destinatarios_atual)
    titulo = st.text_input("Título do email:", value=titulo_atual)
    corpo = st.text_area("Digite o email:", value=corpo_atual, height=400)

    col1, col2, col3 = st.columns(3)
    col1.button(
        "Enviar email",
        use_container_width=True,
        on_click=_enviar_email,
        args=(destinatarios, titulo, corpo, anexos),
    )
    col3.button("Limpar", use_container_width=True, on_click=_limpar)

    # Salvamos no session_state para reaparecer quando o usuário voltar à Home
    st.session_state.destinatarios_atual = destinatarios
    st.session_state.titulo_atual = titulo
    st.session_state.corpo_atual = corpo


def _limpar():
    """
    Limpa somente os campos de destinatários, título e corpo na sessão.
    """
    st.session_state.destinatarios_atual = ""
    st.session_state.titulo_atual = ""
    st.session_state.corpo_atual = ""


def _enviar_email(destinatarios, titulo, corpo, anexos=None):
    """
    Dispara o e-mail, juntando anexos caso existam.
    """
    # Transforma em lista, retirando espaços
    destinatarios = destinatarios.replace(" ", "").split(",")
    email_usuario = _le_email_usuario()
    chave = _le_chave_usuario()

    if email_usuario == "":
        st.error("Adicione email na página de configurações")
        return
    if chave == "":
        st.error("Adicione a chave de email na página de configurações")
        return

    arquivos = []
    if anexos:
        for arquivo in anexos:
            arquivos.append((arquivo.name, arquivo.read()))

    # Chama a função que envia o e-mail (vinda de utilidades.py)
    envia_email(
        email_usuario,
        destinatarios=destinatarios,
        titulo=titulo,
        corpo=corpo,
        senha_app=chave,
        anexos=arquivos,
    )


#
# ============================
#  Página de Templates
# ============================
#
def pag_templates():
    """
    Lista, edita ou remove arquivos de template (arquivos .txt dentro de PASTA_TEMPLATES).
    """
    st.markdown("# Templates")
    st.divider()

    # Percorre todos os arquivos .txt dentro de PASTA_TEMPLATES
    for i, arquivo in enumerate(PASTA_TEMPLATES.glob("*.txt")):
        nome_arquivo = arquivo.stem.replace("_", " ").upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        # Botão para usar o template (carrega conteúdo no corpo do e-mail)
        col1.button(
            nome_arquivo,
            key=f"nome_template_{i}",
            use_container_width=True,
            on_click=_usar_template,
            args=(nome_arquivo,),
        )
        # Botão para editar (abre o mesmo form de criação, mas com texto preenchido)
        col2.button(
            "EDITAR",
            key=f"editar_template_{i}",
            use_container_width=True,
            on_click=_editar_arquivo,
            args=(nome_arquivo,),
        )
        # Botão para remover
        col3.button(
            "REMOVER",
            key=f"remover_template_{i}",
            use_container_width=True,
            on_click=_remove_template,
            args=(nome_arquivo,),
        )

    st.divider()
    st.button(
        "Adicionar Template",
        key="botao_adicionar_template",
        on_click=mudar_pagina,
        args=("adicionar_novo_template",),
    )


def pag_adicionar_novo_template(nome_template="", texto_template=""):
    """
    Form de criação/edição de template. Se vier com 'nome_template' e 'texto_template'
    preenchidos, funciona no modo edição; caso contrário, no modo “criar novo”.
    """
    nome_template = st.text_input("Nome do template", value=nome_template)
    texto_template = st.text_area("Escreva o texto do template", value=texto_template, height=600)
    st.button(
        "Salvar",
        on_click=_salvar_template,
        args=(nome_template, texto_template),
    )


def _usar_template(nome):
    """
    Lê o arquivo .txt do template e coloca no corpo do e-mail; volta à Home.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_TEMPLATES / nome_arquivo
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            texto_arquivo = f.read()
        st.session_state.corpo_atual = texto_arquivo
    mudar_pagina("home")


def _salvar_template(nome, texto):
    """
    Salva (ou sobrescreve) o arquivo de template em PASTA_TEMPLATES.
    """
    PASTA_TEMPLATES.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_TEMPLATES / nome_arquivo, "w", encoding="utf-8") as f:
        f.write(texto)
    mudar_pagina("templates")


def _remove_template(nome):
    """
    Remove o arquivo de template de PASTA_TEMPLATES.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_TEMPLATES / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina("templates")


def _editar_arquivo(nome):
    """
    Lê o template atual e armazena no session_state para preenchar
    o form de edição na próxima renderização de 'pag_adicionar_novo_template'.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_TEMPLATES / nome_arquivo
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            texto_arquivo = f.read()
        st.session_state.nome_template_editar = nome
        st.session_state.texto_template_editar = texto_arquivo
    mudar_pagina("adicionar_novo_template")


#
# ============================
#  Página de Lista de Emails
# ============================
#
def pag_lista_email():
    """
    Lista, edita ou remove arquivos de lista de e-mail (txts dentro de PASTA_LISTA_EMAILS).
    Cada arquivo deve conter e-mails separados por vírgula.
    """
    st.markdown("# Lista Email")
    st.divider()

    for i, arquivo in enumerate(PASTA_LISTA_EMAILS.glob("*.txt")):
        nome_arquivo = arquivo.stem.replace("_", " ").upper()
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        col1.button(
            nome_arquivo,
            key=f"nome_lista_{i}",
            use_container_width=True,
            on_click=_usa_lista,
            args=(nome_arquivo,),
        )
        col2.button(
            "EDITAR",
            key=f"editar_lista_{i}",
            use_container_width=True,
            on_click=_editar_lista,
            args=(nome_arquivo,),
        )
        col3.button(
            "REMOVER",
            key=f"remover_lista_{i}",
            use_container_width=True,
            on_click=_remove_lista,
            args=(nome_arquivo,),
        )

    st.divider()
    st.button(
        "Adiciona Lista",
        key="botao_adicionar_lista",
        on_click=mudar_pagina,
        args=("adicionar_nova_lista",),
    )


def pag_adicionar_nova_lista(nome_lista="", emails_lista=""):
    """
    Form para criação/edição de listas de e-mail. Cada lista é apenas um .txt
    com e-mails separados por vírgula.
    """
    nome_lista = st.text_input("Nome da lista:", value=nome_lista)
    emails_lista = st.text_area("Escreva os emails separados por vírgula:", value=emails_lista, height=600)
    st.button(
        "Salvar",
        on_click=_salvar_lista,
        args=(nome_lista, emails_lista),
    )


def _usa_lista(nome):
    """
    Carrega o conteúdo (string de e-mails) de uma lista e já coloca em
    st.session_state.destinatarios_atual, para usar diretamente na Home.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_LISTA_EMAILS / nome_arquivo
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            texto_arquivo = f.read()
        st.session_state.destinatarios_atual = texto_arquivo
    mudar_pagina("home")


def _salvar_lista(nome, texto):
    """
    Salva (ou sobrescreve) a lista em PASTA_LISTA_EMAILS como .txt.
    """
    PASTA_LISTA_EMAILS.mkdir(exist_ok=True)
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    with open(PASTA_LISTA_EMAILS / nome_arquivo, "w", encoding="utf-8") as f:
        f.write(texto)
    mudar_pagina("lista_emails")


def _remove_lista(nome):
    """
    Remove o arquivo de lista de e-mail de PASTA_LISTA_EMAILS.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_LISTA_EMAILS / nome_arquivo
    if caminho.exists():
        caminho.unlink()
    mudar_pagina("lista_emails")


def _editar_lista(nome):
    """
    Lê a lista de e-mail existente e guarda no session_state para
    pré-preencher o form de edição.
    """
    nome_arquivo = nome.replace(" ", "_").lower() + ".txt"
    caminho = PASTA_LISTA_EMAILS / nome_arquivo
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            texto_arquivo = f.read()
        st.session_state.nome_lista_editar = nome
        st.session_state.texto_lista_editar = texto_arquivo
    mudar_pagina("adicionar_nova_lista")


#
# ============================
#  Página de Configurações
# ============================
#
def pag_configuracao():
    """
    Tela onde o usuário pode inserir ou alterar seu e-mail Gmail e a senha de app.
    Esses valores são gravados em PASTA_CONFIGURACOES/email_usuario.txt e chave.txt
    """
    st.markdown("# Configurações")
    dados = {}
    # Tenta carregar a configuração atual (pode retornar {} caso não exista)
    if (PASTA_CONFIGURACOES / "email_usuario.txt").exists():
        with open(PASTA_CONFIGURACOES / "email_usuario.txt", "r", encoding="utf-8") as f:
            dados["email_usuario"] = f.read()
    else:
        dados["email_usuario"] = ""

    if (PASTA_CONFIGURACOES / "chave.txt").exists():
        with open(PASTA_CONFIGURACOES / "chave.txt", "r", encoding="utf-8") as f:
            dados["chave_email"] = f.read()
    else:
        dados["chave_email"] = ""

    email = st.text_input("Digite o seu email:", value=dados["email_usuario"])
    chave = st.text_input("Digite a chave de email:", value=dados["chave_email"])
    st.button(
        "Salvar",
        key="salvar_config",
        on_click=salvar_configuracao,
        args=(email, chave),
    )


#
# ============================
#  Funções auxiliares para página de templates e listas
#    (elas apenas delegam ao módulo `banco.py`)
# ============================
#
def salvar_configuracao(email, chave):
    """
    Salva os valores em disco: PASTA_CONFIGURACOES/email_usuario.txt e chave.txt
    """
    PASTA_CONFIGURACOES.mkdir(exist_ok=True)
    with open(PASTA_CONFIGURACOES / "email_usuario.txt", "w", encoding="utf-8") as f:
        f.write(email)
    with open(PASTA_CONFIGURACOES / "chave.txt", "w", encoding="utf-8") as f:
        f.write(chave)
    st.success("Configurações salvas!")


#
# ============================
#  Função principal (main)
# ============================
#
def main():
    inicializacao()

    # Menu lateral
    st.sidebar.button("Central de Emails", use_container_width=True, on_click=mudar_pagina, args=("home",))
    st.sidebar.button("Templates", use_container_width=True, on_click=mudar_pagina, args=("templates",))
    st.sidebar.button("Lista de Emails", use_container_width=True, on_click=mudar_pagina, args=("lista_emails",))
    st.sidebar.button("Configuração", use_container_width=True, on_click=mudar_pagina, args=("configuracao",))

    # Renderiza a página correta de acordo com o session_state
    pagina = st.session_state.pagina_central_email
    if pagina == "home":
        home()
    elif pagina == "templates":
        pag_templates()
    elif pagina == "adicionar_novo_template":
        pag_adicionar_novo_template(
            st.session_state.get("nome_template_editar", ""),
            st.session_state.get("texto_template_editar", ""),
        )
    elif pagina == "lista_emails":
        pag_lista_email()
    elif pagina == "adicionar_nova_lista":
        pag_adicionar_nova_lista(
            st.session_state.get("nome_lista_editar", ""),
            st.session_state.get("texto_lista_editar", ""),
        )
    elif pagina == "configuracao":
        pag_configuracao()


if __name__ == "__main__":
    main()
