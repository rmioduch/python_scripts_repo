import sqlite3

DATABASE_FILE = "test_financial_data.db"
EXPORT_FILE = "financial_data_insert.sql"

def export_table_to_sql(cursor, table_name, file):
    file.write(f"-- Eksport tabeli {table_name}\n")
    for row in cursor.execute(f"SELECT * FROM {table_name}"):
        values = ', '.join(
            "NULL" if value is None else f"'{str(value)}'" if isinstance(value, str) else str(value)
            for value in row
        )
        sql = f"INSERT INTO {table_name} VALUES ({values});\n"
        file.write(sql)
    file.write("\n")


def export_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        tables = ["assets", "assets_history", "liabilities", "liabilities_history", "receivables", "receivables_history"]
        for table in tables:
            export_table_to_sql(cursor, table, f)

    conn.close()
    print(f"Dane zapisane w pliku: {EXPORT_FILE}")

if __name__ == "__main__":
    print(f"Eksport danych z bazy: {DATABASE_FILE}...")
    export_database()
