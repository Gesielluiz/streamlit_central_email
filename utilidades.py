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
PASTA_CONFIGURACOES.mkdir(exist_ok=True)

def _le_email_usuario():
    arquivo = PASTA_CONFIGURACOES / "email_usuario.txt"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip()
    return ""

def _le_chave_usuario():
    arquivo = PASTA_CONFIGURACOES / "chave.txt"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip()
    return ""

# ============================
#  Envio de E-mail (com anexos)
# ============================
def envia_email(email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None):
    """
    Monta uma mensagem e envia via SMTP_SSL.
    - destinatarios: lista de strings
    - anexos: list of (filename, bytes)
    """
    # 1) Cria o EmailMessage e preenche cabeçalhos
    msg = EmailMessage()
    msg["From"] = email_usuario
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = titulo
    msg.set_content(corpo)  # corpo em texto simples

    # 2) Adiciona anexos, se houver
    anexos = anexos or []
    for nome_arquivo, conteudo in anexos:
        msg.add_attachment(
            conteudo,
            maintype="application",
            subtype="octet-stream",
            filename=nome_arquivo,
        )

    # 3) Envia via SMTP_SSL

import ssl
import smtplib

context = ssl.create_default_context()
try:
    with smtplib.SMTP("smtp.kinghost.net", 587) as smtp:
        smtp.starttls(context=context)
        smtp.login(email_usuario, senha_app)
        smtp.send_message(msg)
        st.success("Email enviado com sucesso!")
except Exception as e:
    st.error(f"Erro ao enviar o email: {e}")


