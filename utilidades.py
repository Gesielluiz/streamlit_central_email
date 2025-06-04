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
    #    Você poderá salvá-lo num banco ou num CSV para depois correlacionar quem abriu.
    email_id = str(uuid.uuid4())

    # 2) Montar a parte “plain text” (simples) do corpo
    texto_simples = corpo + "\n\n[Para ver imagens, habilite HTML no seu cliente de e-mail]"

    # 3) Montar a parte “HTML” do corpo, incluindo o pixel de rastreamento
    #    Ajuste a URL abaixo para apontar ao endereço público+porta do seu Flask:
    #
    #    Exemplo de URL de rastreamento:
    #      http://<SEU_HOST>:<SUA_PORTA>/rastreamento?id=<email_id>
    #
    #    NOTE: Se estiver em desenvolvimento local, pode usar “localhost” e porta 5000,
    #    mas lembre-se de que, em produção, isso deve virar algo como:
    #      https://meu-dominio.com/rastreamento?id=<email_id>
    #
    host_pixel = "http://localhost:5000"           # <<< ajuste para o seu domínio e porta do Flask
    url_pixel = f"{host_pixel}/rastreamento?id={email_id}"
    cid_pixel = make_msgid(domain="pixel")  # Gera um Content-ID se você quiser embutir via cid: no HTML

    html_body = f"""
    <html>
      <body>
        <div style="font-family: sans-serif; line-height: 1.5;">
          {corpo.replace('\n', '<br>')}<br><br>
          <!-- Pixel de rastreamento transparente (1x1) -->
          <img src="{url_pixel}" width="1" height="1" style="display:none;" alt="." />
        </div>
      </body>
    </html>
    """

    # 4) Começar a montar a mensagem (multipart)
    message = EmailMessage()
    message["From"] = email_usuario
    message["To"] = ", ".join(destinatarios)
    message["Subject"] = titulo

    # Adiciona primeiro a parte de texto simples:
    message.set_content(texto_simples)

    # Em seguida, adiciona a parte HTML (como alternativa)
    message.add_alternative(html_body, subtype="html")

    # 5) Anexar arquivos, se houver
    if anexos:
        for nome_arquivo, conteudo in anexos:
            # Extrai extensão (ex: ".pdf") para tentar deduzir o subtype; mas aqui
            # usamos simplesmente octet-stream para forçar download:
            message.add_attachment(
                conteudo,
                maintype="application",
                subtype="octet-stream",
                filename=nome_arquivo,
            )

    # 6) Enviar por SMTP_SSL (Gmail)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_usuario, senha_app)
            smtp.send_message(message)
        st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar o email: {e}")
        return

    # ---------- Opcional: você pode salvar esse `email_id` num CSV local para
    # posterior consulta (por ex., salvar em “logs/envios.csv” com timestamp, destinatários, etc).
    #
    # Exemplo simples de escrita local (opcional):
    #
    # from datetime import datetime
    # LOGS_ENVIO = Path(__file__).parent / "logs_envios.csv"
    # cabeçalho = not LOGS_ENVIO.exists()
    # with open(LOGS_ENVIO, "a", encoding="utf-8", newline="") as f:
    #     writer = csv.writer(f)
    #     if cabeçalho:
    #         writer.writerow(["email_id", "destinatarios", "titulo", "data_envio"])
    #     writer.writerow([email_id, ";".join(destinatarios), titulo, datetime.now().isoformat()])
    #
    # Assim você sabe que gerou o pixel para aquele ID em determinada hora.


# ============================
#  Outras funções de navegação (se necessário)
# ============================
# — já definidas acima: mudar_pagina(), _le_email_usuario(), _le_chave_usuario()
#
