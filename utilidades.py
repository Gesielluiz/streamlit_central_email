import ssl
import smtplib
import streamlit as st
from email.message import EmailMessage
from pathlib import Path

# pasta onde guardo email+senha
PASTA_CONFIGURACOES = Path(__file__).parent / "configuracoes"
PASTA_CONFIGURACOES.mkdir(parents=True, exist_ok=True)

def mudar_pagina(nome_pagina):
    st.session_state.pagina_central_email = nome_pagina

def _salvar_email(email: str):
    with open(PASTA_CONFIGURACOES / "email_usuario.txt", "w", encoding="utf-8") as f:
        f.write(email.strip())

def _salvar_chave(chave: str):
    with open(PASTA_CONFIGURACOES / "chave.txt", "w", encoding="utf-8") as f:
        f.write(chave.strip())

def _le_email_usuario() -> str:
    arquivo = PASTA_CONFIGURACOES / "email_usuario.txt"
    return arquivo.read_text(encoding="utf-8").strip() if arquivo.exists() else ""

def _le_chave_usuario() -> str:
    arquivo = PASTA_CONFIGURACOES / "chave.txt"
    return arquivo.read_text(encoding="utf-8").strip() if arquivo.exists() else ""

def envia_email(
    email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None
):
    """
    Envia pelo KingHost via SSL implícito (porta 465).
    """
    msg = EmailMessage()
    msg["From"]    = email_usuario
    msg["To"]      = ", ".join(destinatarios)
    msg["Subject"] = titulo
    msg.set_content(corpo)

    # adiciona anexos, se houver
    if anexos:
        for nome, dados in anexos:
            msg.add_attachment(
                dados,
                maintype="application",
                subtype="octet-stream",
                filename=nome,
            )

    context = ssl.create_default_context()
    try:
        # conecta com SSL na 465
        with smtplib.SMTP_SSL(
            host="smtp.kinghost.net",
            port=465,
            context=context,
            timeout=10
        ) as smtp:
            smtp.ehlo()
            smtp.login(email_usuario, senha_app)
            smtp.send_message(msg)

        st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e‑mail: {e}")
