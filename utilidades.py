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
    """
    Lê o email do usuário a partir de `configuracoes/email_usuario.txt`.
    Se não existir, retorna string vazia.
    """
    arquivo = PASTA_CONFIGURACOES / "email_usuario.txt"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip()
    return ""

def _le_chave_usuario():
    """
    Lê a chave de app do usuário a partir de `configuracoes/chave.txt`.
    Se não existir, retorna string vazia.
    """
    arquivo = PASTA_CONFIGURACOES / "chave.txt"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip()
    return ""


# ============================
#  Envio de E-mail com Anexos + Pixel de Rastreamento
# ============================
def envia_email(email_usuario, destinatarios, titulo, corpo, senha_app, anexos=None):
    """
    Monta uma mensagem multipart (texto simples + HTML com pixel de rastreio) e envia via
    Gmail SSL. Se houver lista de anexos (nome, bytes), adiciona cada um como attachment.

    - `destinatarios` deve ser uma lista de strings, ex: ["email1@dominio.com", "email2@dominio.com"]
    - `anexos` (opcional) deve ser algo como: [("arquivo.pdf", b"conteúdo em bytes"), ...]
    """

    # 1) Gerar um ID único para este e-mail, que será usado na URL de rastreamento.
    email_id = str(uuid.uuid4())

    # 2) Montar a parte “plain text” (simples) do corpo
    texto_simples = corpo + "\n\n[Para visualizar este e-mail corretamente, habilite HTML no seu cliente de e-mail.]"

    # 3) Montar a parte “HTML” do corpo, incluindo o pixel de rastreamento invisível
    #
    #    Ajuste a URL abaixo para apontar ao endereço público + porta do seu Flask:
    #      exemplo: "https://meu-dominio.up.railway.app:5005"
    #
    host_pixel = "http://localhost:5000"  # <<< ALTERE para o seu domínio/porta Flask em produção!
    url_pixel = f"{host_pixel}/rastreamento?id={email_id}"

    # Opcional: gerar um Content-ID (caso queira usar <img src="cid:..."> em vez de URL direta)
    cid_pixel = make_msgid(domain="pixel_tracking")

    # Corpo HTML (com nova linha convertida em <br>, e pixel de rastreamento)
    html_body = f"""
    <html>
      <body style="font-family: sans-serif; line-height: 1.5;">
        {corpo.replace('\n', '<br>')}<br><br>
        <!-- Pixel de rastreamento transparente (1x1) -->
        <img src="{url_pixel}" width="1" height="1" style="display:none;" alt="." />
      </body>
    </html>
    """

    # 4) Caso queira usar CID em vez de URL, substitua a tag <img> acima por:
    #    <img src="cid:{cid_pixel[1:-1]}" width="1" height="1" style="display:none;" alt="." />
    #
    #    E depois faça message_email.get_payload()[1].add_related( conteúdo_do_pixel, ... )
    #    Mas aqui vamos usar apenas URL diretamente.

    # 5) Criar o EmailMessage multipart/alternative
    message_email = EmailMessage()
    message_email["From"] = email_usuario
    message_email["To"] = ", ".join(destinatarios)
    message_email["Subject"] = titulo

    # 6) Parte Texto simples
    message_email.set_content(texto_simples)

    # 7) Parte HTML (fallback é o texto simples acima)
    message_email.add_alternative(html_body, subtype="html")

    # 8) Anexos, se houverem
    if anexos:
        for nome_arquivo, conteudo in anexos:
            message_email.add_attachment(
                conteudo,
                maintype="application",
                subtype="octet-stream",
                filename=nome_arquivo
            )

    # 9) Enviar via SMTP SSL (Gmail)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(message_email)
            st.success("E-mail enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o e-mail: {e}")
