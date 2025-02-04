import sqlite3

DATABASE_FILE = "test_transactions.db"
EXPORT_FILE = "transactions_insert.sql"

conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

with open(EXPORT_FILE, "w") as f:
    for row in cursor.execute("SELECT * FROM transactions"):
        sql = f"INSERT INTO transactions (id, date, amount, category, type, description) VALUES {row};\n"
        f.write(sql)

conn.close()
print(f"Zapisano eksport do {EXPORT_FILE}")
