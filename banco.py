# banco.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def conectar():
    """
    Conecta usando a variável de ambiente DATABASE_URL.
    """
    url = os.getenv("DATABASE_URL")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

# ========== CONFIGURAÇÃO ==========
def salvar_configuracao(email, chave):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM configuracao;")
    cur.execute(
        "INSERT INTO configuracao (email_usuario, chave_email) VALUES (%s, %s);",
        (email, chave),
    )
    conn.commit()
    cur.close()
    conn.close()

def carregar_configuracao():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT email_usuario, chave_email FROM configuracao LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result or {"email_usuario": "", "chave_email": ""}

# ========== TEMPLATE ==========
def salvar_template(nome, texto):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO template (nome_template, texto_template) VALUES (%s, %s);",
        (nome, texto),
    )
    conn.commit()
    cur.close()
    conn.close()

def listar_templates():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nome_template, texto_template FROM template;")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado

def remover_template(nome):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM template WHERE nome_template = %s;", (nome,))
    conn.commit()
    cur.close()
    conn.close()

def carregar_template(nome):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "SELECT texto_template FROM template WHERE nome_template = %s;", (nome,)
    )
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado["texto_template"] if resultado else ""

# ========== LISTA DE EMAIL ==========
def salvar_lista(nome, emails):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO lista_email (nome_lista, emails_lista) VALUES (%s, %s);",
        (nome, emails),
    )
    conn.commit()
    cur.close()
    conn.close()

def listar_listas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nome_lista, emails_lista FROM lista_email;")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado

def remover_lista(nome):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM lista_email WHERE nome_lista = %s;", (nome,))
    conn.commit()
    cur.close()
    conn.close()

def carregar_lista(nome):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "SELECT emails_lista FROM lista_email WHERE nome_lista = %s;", (nome,)
    )
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado["emails_lista"] if resultado else ""

# ========== E-Mails Enviado ==========

def salvar_email_enviado(destinatario, titulo, corpo, rastreio_id):
    """
    Grava um disparo na tabela email_enviado.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        # Troque "e-mails enviado" pelo nome correto da tabela no seu DB
        """
        INSERT INTO email_enviado
          (destinatario, titulo, corpo, rastreio_id)
        VALUES (%s, %s, %s, %s);
        """,
        (destinatario, titulo, corpo, rastreio_id)
    )
    conn.commit()
    cur.close()
    conn.close()


# ========== RASTREAMENTO ==========
def listar_rastreamentos():
    """
    Retorna todos os eventos de rastreamento,
    fazendo join com a tabela 'e-mails enviado' para exibir
    também o destinatário e o título.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
          r.id,
          e.destinatario,
          e.titulo,
          r.rastreio_id,
          r.ip,
          r.user_agent,
          r.data_hora
        FROM rastreamento AS r
        INNER JOIN email_enviado AS e
          ON r.rastreio_id = e.rastreio_id
        ORDER BY r.data_hora DESC;
        """
    )
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    # Converte cada registro em dict para o Streamlit exibir facilmente
    colunas = ["id", "destinatario", "titulo", "rastreio_id", "ip", "user_agent", "data_hora"]
    lista_dicts = [dict(zip(colunas, linha)) for linha in resultado]
    return lista_dicts

