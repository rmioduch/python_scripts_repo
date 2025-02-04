import sqlite3

DATABASE_FILE = "test_transactions_copy.db"
EXPORT_FILE = "transactions_insert.sql"

conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

# Usunięcie wszystkich rekordów przed importem
cursor.execute("DELETE FROM transactions")
conn.commit()

# Wczytanie danych z pliku SQL
with open(EXPORT_FILE, "r") as f:
    sql_script = f.read()
    cursor.executescript(sql_script)

conn.commit()
conn.close()
print("Import zakończony")
