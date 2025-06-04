# banco.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ========== Conexão com o banco ==========
def conectar():
    """
    Abre uma conexão usando a variável de ambiente DATABASE_URL.
    Retorna um objeto psycopg2.Connection com cursor do tipo RealDictCursor.
    """
    url = os.getenv("DATABASE_URL")
    if url is None:
        raise RuntimeError("A variável de ambiente DATABASE_URL não está definida.")
    return psycopg2.connect(url, cursor_factory=RealDictCursor)


# ========== CONFIGURAÇÃO ==========
def salvar_configuracao(email, chave):
    """
    Apaga qualquer configuração anterior e insere um único registro
    na tabela `configuracao` com (email_usuario, chave_email).
    """
    conn = conectar()
    cur = conn.cursor()
    # Garante que exista apenas uma linha na tabela de configuração
    cur.execute("DELETE FROM configuracao;")
    cur.execute(
        "INSERT INTO configuracao (email_usuario, chave_email) VALUES (%s, %s);",
        (email, chave),
    )
    conn.commit()
    cur.close()
    conn.close()


def carregar_configuracao():
    """
    Carrega o único registro da tabela `configuracao`.
    Se não houver nada, retorna um dicionário com strings vazias.
    Exemplo de retorno:
      {"email_usuario": "meuemail@gmail.com", "chave_email": "abcd1234"}
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM configuracao LIMIT 1;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        # result virá em formato RealDictCursor, ou seja, dicionário.
        return result
    else:
        return {"email_usuario": "", "chave_email": ""}


# ========== TEMPLATE ==========
def salvar_template(nome, texto):
    """
    Insere um novo template (nome_template, texto_template) na tabela `template`.
    """
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
    """
    Retorna uma lista de dicionários (RealDictCursor) contendo todos os registros
    da tabela `template`. Cada item tem as chaves: id, nome_template, texto_template.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM template;")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado  # lista de dicts, ex: [{"id": 1, "nome_template": "...", "texto_template": "..."}]


def remover_template(nome):
    """
    Deleta o(s) registro(s) cujo nome_template seja igual a `nome`.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM template WHERE nome_template = %s;", (nome,))
    conn.commit()
    cur.close()
    conn.close()


def carregar_template(nome):
    """
    Busca o campo texto_template para o registro cujo nome_template = nome.
    Retorna a string do template ou "" se não encontrar nada.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT texto_template FROM template WHERE nome_template = %s;", (nome,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    if resultado:
        return resultado["texto_template"]
    else:
        return ""


# ========== LISTAS DE EMAIL ==========
def salvar_lista(nome, emails):
    """
    Insere um novo registro na tabela `lista_email` ( nome_lista, emails_lista ).
    """
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
    """
    Retorna todos os registros da tabela `lista_email`.
    Cada item é um dicionário com as chaves: id, nome_lista, emails_lista.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lista_email;")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return resultado


def remover_lista(nome):
    """
    Deleta qualquer registro em `lista_email` cujo nome_lista seja igual a `nome`.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM lista_email WHERE nome_lista = %s;", (nome,))
    conn.commit()
    cur.close()
    conn.close()


def carregar_lista(nome):
    """
    Busca emails_lista (string) para o registro cujo nome_lista = nome.
    Se não encontrar, retorna string vazia.
    """
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT emails_lista FROM lista_email WHERE nome_lista = %s;", (nome,))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    if resultado:
        return resultado["emails_lista"]
    else:
        return ""
