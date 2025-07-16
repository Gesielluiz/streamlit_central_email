import ssl
import smtplib
import socket
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
def envia_email(
    email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None
):
    """
    Monta a mensagem e envia usando KingHost (STARTTLS na porta 587),
    forçando resolução IPv4 para evitar Errno 99.
    """
    # 1) Prepara o EmailMessage
    msg = EmailMessage()
    msg["From"]    = email_usuario
    msg["To"]      = ", ".join(destinatarios)
    msg["Subject"] = titulo
    msg.set_content(corpo)

    # 2) Anexos (se houver)
    if anexos:
        for nome, dados in anexos:
            msg.add_attachment(
                dados,
                maintype="application",
                subtype="octet-stream",
                filename=nome,
            )

    # 3) Contexto TLS
    context = ssl.create_default_context()

    try:
        # 4) Resolve apenas IPv4 para smtp.kinghost.net:587
        infos = socket.getaddrinfo(
            "smtp.kinghost.net",
            587,
            socket.AF_INET,          # só IPv4
            socket.SOCK_STREAM
        )
        ipv4_addr, ipv4_port = infos[0][4]

        # 5) Conecta manualmente ao IPv4
        smtp = smtplib.SMTP(timeout=10)
        smtp.connect(ipv4_addr, ipv4_port)
        smtp.starttls(context=context)
        smtp.login(email_usuario, senha_app)
        smtp.send_message(msg)
        smtp.quit()

        st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e‑mail: {e}")
