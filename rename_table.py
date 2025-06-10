
# rename_table.py
import os
import psycopg2
from psycopg2 import sql

# Usa a mesma URL de conexão que seu app Streamlit usa
DATABASE_URL = os.getenv("https://web-production-5e67a.up.railway.app/")

def main():
    if not DATABASE_URL:
        print("❌ A variável DATABASE_URL não está definida.")
        return

    # Conecta ao banco
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Renomeia a tabela de "e-mails enviado" para email_enviado
    cur.execute(
        sql.SQL('ALTER TABLE {old} RENAME TO {new}')
           .format(
             old=sql.Identifier('e-mails enviado'),
             new=sql.Identifier('email_enviado'),
           )
    )
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabela renomeada para email_enviado!")

if __name__ == "__main__":
    main()
