# rename_table.py
import os
import psycopg2
from psycopg2 import sql

# Puxa a URL do seu banco a partir da env var setada pelo Railway
DATABASE_URL = os.getenv("DATABASE_URL")

def main():
    if not DATABASE_URL:
        print("❌ A variável DATABASE_URL não está definida.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Renomeia a tabela antiga "e-mails enviado" para email_enviado
    cur.execute(
        sql.SQL('ALTER TABLE {old} RENAME TO {new}').format(
            old=sql.Identifier('e-mails enviado'),
            new=sql.Identifier('email_enviado'),
        )
    )
    conn.commit()
    cur.close()
    conn.close()

    print("✅ Tabela renomeada para email_enviado com sucesso!")

if __name__ == "__main__":
    main()

