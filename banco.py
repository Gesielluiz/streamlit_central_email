
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def conectar():
    url = os.getenv("DATABASE_URL")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

# ========== CONFIGURAÇÃO ==========
def salvar_configuracao(email, chave):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM configuracao;")
    cur.execute("INSERT INTO configuracao (email_usuario, chave_email) VALUES (%s, %s);", (email, chave))
    conn.commit()
    cur.close()
    conn.close()

def carregar_configuracao():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM configuracao LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result or {"email_usuario": "", "chave_email": ""}

# ========== TEMPLATE ==========
def salvar_template(nome, texto):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO template (nome_template, texto_template) VALUES (%s, %s);", (nome, texto))
    conn.commit()
    cur.close()
    conn.close()

def listar_templates():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM template;")
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
    cur.execute("SELECT texto_template FROM template WHERE nome_template = %s;", (nome,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado["texto_template"] if resultado else ""

# ========== LISTAS DE EMAIL ==========
def salvar_lista(nome, emails):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO lista_email (nome_lista, emails_lista) VALUES (%s, %s);", (nome, emails))
    conn.commit()
    cur.close()
    conn.close()

def listar_listas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lista_email;")
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
    cur.execute("SELECT emails_lista FROM lista_email WHERE nome_lista = %s;", (nome,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado["emails_lista"] if resultado else ""
