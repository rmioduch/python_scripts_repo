import sqlite3
import random
import datetime

DATABASE_FILE = "test_financial_data.db"
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

# Tworzenie tabeli dla aktywów
cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,  -- Typ aktywa (np. "Akcje", "Nieruchomość")
    category TEXT NOT NULL,  -- Kategoria (np. "Inwestycyjne", "Osobiste")
    amount REAL NOT NULL,  -- Wartość aktywa
    description TEXT,  -- Opis aktywa (np. nazwa banku, numer konta)
    state_as_of_date TEXT NOT NULL,  -- Data aktualizacji w formacie YYYY-MM-DD
    currency TEXT NOT NULL  -- Waluta (np. "PLN", "USD", "EUR")
)
""")

# Tworzenie tabeli dla zobowiązań
cursor.execute("""
CREATE TABLE IF NOT EXISTS liabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,  -- Typ zobowiązania (np. "Kredyt", "Pożyczka")
    amount REAL NOT NULL,  -- Kwota zobowiązania
    description TEXT,  -- Opis zobowiązania
    due_date TEXT NOT NULL,  -- Termin spłaty w formacie YYYY-MM-DD
    currency TEXT NOT NULL  -- Waluta (np. "PLN", "USD", "EUR")
)
""")

# Tworzenie tabeli dla należności
cursor.execute("""
CREATE TABLE IF NOT EXISTS receivables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debtor TEXT NOT NULL,  -- Osoba/Firma, która jest dłużnikiem
    amount REAL NOT NULL,  -- Kwota należności
    loan_date TEXT NOT NULL,  -- Data pożyczki w formacie YYYY-MM-DD
    due_date TEXT NOT NULL,  -- Termin zwrotu w formacie YYYY-MM-DD
    status TEXT NOT NULL,  -- Status (np. "Spłacone", "W trakcie")
    currency TEXT NOT NULL  -- Waluta (np. "PLN", "USD", "EUR")
)
""")

# Tworzenie tabeli dla historii zmian aktywów
cursor.execute("""
CREATE TABLE IF NOT EXISTS assets_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,  -- Odwołanie do tabeli assets
    type TEXT NOT NULL,  -- Typ aktywa
    category TEXT NOT NULL,  -- Kategoria aktywa
    amount REAL NOT NULL,  -- Wartość aktywa
    state_as_of_date TEXT NOT NULL,  -- Data aktualizacji
    description TEXT,  -- Opis aktywa
    currency TEXT NOT NULL,  -- Waluta
    converted_amount REAL,  -- Przeliczona wartość w walucie bazowej
    change_date TEXT NOT NULL,  -- Data zmiany
    change_type TEXT NOT NULL,  -- Typ zmiany (INSERT, UPDATE, DELETE)
    FOREIGN KEY (asset_id) REFERENCES assets(id)
)
""")

# Tworzenie tabeli dla historii zmian zobowiązań
cursor.execute("""
CREATE TABLE IF NOT EXISTS liabilities_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    liability_id INTEGER NOT NULL,  -- Odwołanie do tabeli liabilities
    type TEXT NOT NULL,  -- Typ zobowiązania
    amount REAL NOT NULL,  -- Kwota zobowiązania
    description TEXT,  -- Opis zobowiązania
    due_date TEXT NOT NULL,  -- Termin spłaty
    currency TEXT NOT NULL,  -- Waluta
    converted_amount REAL,  -- Przeliczona wartość w walucie bazowej
    change_date TEXT NOT NULL,  -- Data zmiany
    change_type TEXT NOT NULL,  -- Typ zmiany (INSERT, UPDATE, DELETE)
    FOREIGN KEY (liability_id) REFERENCES liabilities(id)
)
""")

# Tworzenie tabeli dla historii zmian należności
cursor.execute("""
CREATE TABLE IF NOT EXISTS receivables_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receivable_id INTEGER NOT NULL,  -- Odwołanie do tabeli receivables
    debtor TEXT NOT NULL,  -- Osoba/Firma, która jest dłużnikiem
    amount REAL NOT NULL,  -- Kwota należności
    loan_date TEXT NOT NULL,  -- Data pożyczki
    due_date TEXT NOT NULL,  -- Termin zwrotu
    status TEXT NOT NULL,  -- Status
    currency TEXT NOT NULL,  -- Waluta
    converted_amount REAL,  -- Przeliczona wartość w walucie bazowej
    change_date TEXT NOT NULL,  -- Data zmiany
    change_type TEXT NOT NULL,  -- Typ zmiany (INSERT, UPDATE, DELETE)
    FOREIGN KEY (receivable_id) REFERENCES receivables(id)
)
""")

def generate_random_date(year, month=None):
    if month:
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, 28)
    else:
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
    delta = end_date - start_date
    return (start_date + datetime.timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

def insert_assets():
    assets = [
        ("Akcje", "Inwestycyjne", 200000, "Portfolio giełdowe", "PLN"),
        ("Obligacje", "Inwestycyjne", 150000, "Obligacje korporacyjne", "PLN"),
        ("Obligacje skarbowe", "Inwestycyjne", 150000, "Obligacje skarbowe RP", "PLN"),
        ("Fundusze Inwestycyjne", "Inwestycyjne", 150000, "Fundusze inwestycyjne globalne", "PLN"),
        ("Nieruchomości Inwestycyjne", "Inwestycyjne", 300000, "Mieszkanie na wynajem", "PLN"),
        ("Kryptowaluty", "Inwestycyjne", 50000, "Portfel kryptowalut", "USD"),
        ("Metale Szlachetne", "Inwestycyjne", 50000, "Złoto, srebro", "PLN"),
        ("Samochód", "Osobiste", 100000, "Pojazd osobowy", "PLN"),
        ("Nieruchomość Mieszkalna", "Osobiste", 900000, "Dom rodzinny", "PLN"),
        ("Rachunek bankowy", "Osobiste", 100000, "Konto w PLN", "PLN"),
        ("Rachunek bankowy - walutowy", "Inwestycyjne", 100000, "Konto w EUR", "EUR")
    ]

    for asset in assets:
        cursor.execute("""
        INSERT INTO assets (type, category, amount, description, state_as_of_date, currency)
        VALUES (?, ?, ?, ?, ?, ?)""",
                       (asset[0], asset[1], asset[2], asset[3], generate_random_date(2025), asset[4]))

    conn.commit()
    insert_assets_history()

def insert_assets_history():
    cursor.execute("SELECT id, type, category, amount, description, currency FROM assets")
    asset_data = cursor.fetchall()

    exchange_rates = {"USD": 4.0, "EUR": 4.5, "PLN": 1.0}  # Przykładowe kursy walut

    for asset_id, asset_type, category, initial_amount, description, currency in asset_data:
        previous_amount = initial_amount
        for year in range(2015, 2025):
            change = round(random.uniform(-10000, 15000), 2)
            new_amount = max(0, previous_amount + change)
            converted_value = new_amount * exchange_rates.get(currency, 1.0)  # Konwersja na PLN
            change_type = "INCREASE" if change >= 0 else "DECREASE"

            cursor.execute("""
            INSERT INTO assets_history (asset_id, type, category, amount, state_as_of_date, description, currency, converted_amount, change_date, change_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (asset_id, asset_type, category, new_amount, generate_random_date(year), description, currency, converted_value, generate_random_date(year), change_type))

            previous_amount = new_amount  # Aktualizujemy wartość dla następnego wpisu

        # Dodajemy finalną wartość na koniec roku 2024
        cursor.execute("""
        INSERT INTO assets_history (asset_id, type, category, amount, state_as_of_date, description, currency, converted_amount, change_date, change_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (asset_id, asset_type, category, initial_amount, "2024-12-31", description, currency, initial_amount * exchange_rates.get(currency, 1.0), "2024-12-31", "FINAL"))

    conn.commit()

def insert_liabilities():
    liabilities = [
        ("Kredyt Hipoteczny", 500000, "Hipoteka", "PLN"),
        ("Pożyczka Osobista", 50000, "Kredyt na remont", "PLN"),
        ("Leasing", 40000, "Leasing samochodowy", "PLN"),
        ("Karta Kredytowa", 20000, "Zadłużenie karty", "USD"),
        ("Faktury do Zapłaty", 10000, "Opłaty miesięczne", "PLN")
    ]

    for liability in liabilities:
        cursor.execute("""
        INSERT INTO liabilities (type, amount, description, due_date, currency)
        VALUES (?, ?, ?, ?, ?)""",
                       (liability[0], liability[1], liability[2], generate_random_date(2030), liability[3]))

    conn.commit()
    insert_liabilities_history()

def insert_liabilities_history():
    cursor.execute("SELECT id, type, amount, description, currency FROM liabilities")
    liability_data = cursor.fetchall()

    exchange_rates = {"USD": 4.0, "EUR": 4.5, "PLN": 1.0}  # Przykładowe kursy walut

    for liability_id, liability_type, initial_amount, description, currency in liability_data:
        previous_amount = initial_amount
        for year in range(2015, 2025):
            change = round(random.uniform(-5000, 10000), 2)
            new_amount = max(0, previous_amount - change)
            converted_value = new_amount * exchange_rates.get(currency, 1.0)  # Konwersja na PLN
            change_type = "PAYMENT" if change >= 0 else "NEW_LOAN"

            cursor.execute("""
            INSERT INTO liabilities_history (liability_id, type, amount, description, due_date, currency, converted_amount, change_date, change_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (liability_id, liability_type, new_amount, description, generate_random_date(year), currency, converted_value, generate_random_date(year), change_type))

            previous_amount = new_amount  # Aktualizujemy wartość dla następnego wpisu

    conn.commit()

def insert_receivables():
    receivables = [
        ("Pożyczka udzielona rodzinie", 10000, "2023-01-01", "2025-01-01", "W trakcie", "PLN"),
        ("Faktura wystawiona firmie", 20000, "2023-02-01", "2023-03-01", "Niespłacone", "PLN"),
        ("Zwrot podatku", 5000, "2023-03-01", "2023-06-01", "Spodziewane", "PLN")
    ]

    for receivable in receivables:
        cursor.execute("""
        INSERT INTO receivables (debtor, amount, loan_date, due_date, status, currency)
        VALUES (?, ?, ?, ?, ?, ?)""",
                       (receivable[0], receivable[1], receivable[2], receivable[3], receivable[4], receivable[5]))

    conn.commit()
    insert_receivables_history()

def insert_receivables_history():
    cursor.execute("SELECT id, debtor, amount, currency FROM receivables")
    receivable_data = cursor.fetchall()

    exchange_rates = {"USD": 4.0, "EUR": 4.5, "PLN": 1.0}  # Przykładowe kursy walut

    for receivable_id, debtor, initial_amount, currency in receivable_data:
        previous_amount = initial_amount
        for year in range(2015, 2025):
            change = round(random.uniform(-1000, 2000), 2)
            new_amount = max(0, previous_amount - change)
            converted_value = new_amount * exchange_rates.get(currency, 1.0)  # Konwersja na PLN
            change_type = "PAYMENT" if change >= 0 else "NEW_LOAN"

            cursor.execute("""
            INSERT INTO receivables_history (receivable_id, debtor, amount, loan_date, due_date, status, currency, converted_amount, change_date, change_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (receivable_id, debtor, new_amount, generate_random_date(year), generate_random_date(year), "W trakcie", currency, converted_value, generate_random_date(year), change_type))

            previous_amount = new_amount  # Aktualizujemy wartość dla następnego wpisu

    conn.commit()

if __name__ == "__main__":
    print("Generowanie danych testowych...")
    insert_assets()
    insert_liabilities()
    insert_receivables()
    print(f"Dane zapisane w bazie: {DATABASE_FILE}")
    conn.close()