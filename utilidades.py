from email.message import EmailMessage
import smtplib
import ssl
from pathlib import Path

import streamlit as st


# Função para mudar de página
def mudar_pagina(nome_pagina):
    st.session_state.pagina_central_email = nome_pagina

def envia_email(remetente, destinatarios, titulo, corpo, senha_app, anexos=None):
    from email.message import EmailMessage
    import smtplib

    msg = EmailMessage()
    msg['Subject'] = titulo
    msg['From'] = remetente
    msg['To'] = ', '.join(destinatarios)
    msg.set_content(corpo)

    if anexos:
        for nome_arquivo, conteudo in anexos:
            msg.add_attachment(conteudo, maintype='application', subtype='octet-stream', filename=nome_arquivo)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(remetente, senha_app)
        smtp.send_message(msg)
