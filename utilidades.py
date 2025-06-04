from email.message import EmailMessage
import smtplib
import ssl
from pathlib import Path
import streamlit as st


# Função para mudar de página
def mudar_pagina(nome_pagina):
    st.session_state.pagina_central_email = nome_pagina


def envia_email(email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None):
    message_email = EmailMessage()
    message_email['From'] = email_usuario
    message_email['To'] = ', '.join(destinatarios)  # <- Junta a lista em string
    message_email['Subject'] = titulo
    message_email.set_content(corpo)

    # Adiciona anexos se houver
    if anexos:
        for nome_arquivo, conteudo in anexos:
            message_email.add_attachment(
                conteudo,
                maintype='application',
                subtype='octet-stream',
                filename=nome_arquivo
            )

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(message_email)
            st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o email: {e}")
