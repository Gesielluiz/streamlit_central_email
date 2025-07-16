# utilidades.py
import ssl
import smtplib
import streamlit as st
from email.message import EmailMessage
from pathlib import Path

# ============================
#  Função para trocar de página
# ============================
def mudar_pagina(nome_pagina):
    st.session_state.pagina_central_email = nome_pagina

# ============================
#  Leitura/Gravação de Configuração
# ============================
PASTA_CONFIGURACOES = Path(__file__).parent / "configuracoes"
PASTA_CONFIGURACOES.mkdir(parents=True, exist_ok=True)

def _salvar_email(email: str):
    try:
        with open(PASTA_CONFIGURACOES / "email_usuario.txt", "w", encoding="utf-8") as f:
            f.write(email.strip())
    except Exception as e:
        st.error(f"Erro ao salvar email: {e}")

def _salvar_chave(chave: str):
    try:
        with open(PASTA_CONFIGURACOES / "chave.txt", "w", encoding="utf-8") as f:
            f.write(chave.strip())
    except Exception as e:
        st.error(f"Erro ao salvar chave: {e}")

def _le_email_usuario() -> str:
    try:
        arquivo = PASTA_CONFIGURACOES / "email_usuario.txt"
        if arquivo.exists():
            return arquivo.read_text(encoding="utf-8").strip()
    except Exception as e:
        st.error(f"Erro ao ler email: {e}")
    return ""

def _le_chave_usuario() -> str:
    try:
        arquivo = PASTA_CONFIGURACOES / "chave.txt"
        if arquivo.exists():
            return arquivo.read_text(encoding="utf-8").strip()
    except Exception as e:
        st.error(f"Erro ao ler chave: {e}")
    return ""

# ============================
#  Envio de E-mail (com anexos)
# ============================
def envia_email(email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None):
    """
    Monta uma mensagem e envia via SMTP (KingHost).
    - destinatarios: lista de strings
    - anexos: list of (filename, bytes)
    """
    msg = EmailMessage()
    msg["From"] = email_usuario
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = titulo
    msg.set_content(corpo)

    anexos = anexos or []
    for nome_arquivo, conteudo in anexos:
        msg.add_attachment(
            conteudo,
            maintype="application",
            subtype="octet-stream",
            filename=nome_arquivo,
        )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.kinghost.net", 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(email_usuario, senha_app)
            smt






