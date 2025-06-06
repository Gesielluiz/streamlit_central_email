# utilidades.py
import uuid
import ssl
import smtplib
import streamlit as st
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

# ============================
#  Função para trocar de página
# ============================
def mudar_pagina(nome_pagina):
    st.session_state.pagina_central_email = nome_pagina

# ============================
#  Leitura/Gravação de Configuração (email + chave em disco)
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
#  Envio de E-mail com Pixel de Rastreamento
# ============================
def envia_email(email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None):
    """
    Monta mensagem multipart (texto simples + HTML com pixel) e envia,
    autenticando no Gmail SSL.
    - destinatarios: lista de strings
    - anexos: [('arquivo.pdf', b'...'), ...]
    """
    # 1) Gera um ID único para este e-mail
    email_id = str(uuid.uuid4())

    # 2) Texto simples
    texto_simples = corpo + "\n\n[Para visualizar imagens, habilite HTML]"

    # 3) Cria o HTML com pixel de rastreamento
    host_pixel = "http://localhost:5000"  # <<<<< Em produção, ajuste para o domínio final
    url_pixel = f"{host_pixel}/rastreamento?id={email_id}"
    html_body = f"""
    <html>
      <body style="font-family: sans-serif; line-height: 1.5;">
        {corpo.replace('\n', '<br>')}<br><br>
        <img src="{url_pixel}" width="1" height="1" style="display:none;" alt="." />
      </body>
    </html>
    """

    # 4) Monta o EmailMessage multipart/alternative
    message_email = EmailMessage()
    message_email["From"] = email_usuario
    message_email["To"] = ", ".join(destinatarios)
    message_email["Subject"] = titulo
    message_email.set_content(texto_simples)         # Parte plain text
    message_email.add_alternative(html_body, subtype="html")  # Parte HTML

    # 5) Adiciona anexos, se houver
    if anexos:
        for nome_arquivo, conteudo in anexos:
            message_email.add_attachment(
                conteudo,
                maintype="application",
                subtype="octet-stream",
                filename=nome_arquivo,
            )

    # 6) Envia via SMTP_SSL
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(message_email)
            st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o email: {e}")
