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
def envia_email(
    email_usuario,
    destinatarios: list[str],
    titulo: str,
    corpo: str,
    senha_app: str,
    anexos: list[tuple[str, bytes]] | None = None,
):
    """
    Monta a mensagem e envia usando KingHost (STARTTLS na porta 587).
    - destinatarios: lista de strings
    - anexos: lista de tuples (nome_arquivo, dados_bytes)
    """
    # 1) Cria o objeto de e‑mail
    msg = EmailMessage()
    msg["From"]    = email_usuario
    msg["To"]      = ", ".join(destinatarios)
    msg["Subject"] = titulo
    msg.set_content(corpo)

    # 2) Anexa arquivos, se houver
    if anexos:
        for nome, conteudo in anexos:
            msg.add_attachment(
                conteudo,
                maintype="application",
                subtype="octet-stream",
                filename=nome,
            )

    # 3) Envia via SMTP STARTTLS (porta 587)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP("smtp.kinghost.net", 587, timeout=10) as smtp:
            smtp.starttls(context=context)
            smtp.login(email_usuario, senha_app)
            smtp.send_message(msg)
        st.success("Email enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar e‑mail: {e}")
