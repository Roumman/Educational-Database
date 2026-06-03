"""
Скрипт инициализации тестовой базы данных для SQL‑тренажёра банковской системы.

Создаёт и заполняет БД тестовыми данными:
* генерирует записи о клиентах;
* создаёт учётные записи с логинами и хешированными паролями;
* формирует счета с начальными балансами;
* добавляет транзакции (пополнения и снятия);
* создаёт записи о кредитах и депозитах.
"""



import sqlite3
import random
from datetime import datetime, timedelta
import hashlib
import os

print("🔎 Скрипт запущен — начинаем инициализацию БД...")

# Тестовые данные
FIRST_NAMES = ['Иван', 'Пётр', 'Сергей']
LAST_NAMES = ['Иванов', 'Петров', 'Сидоров']
PATRONYMICS = ['Иванович', 'Петрович', 'Сергеевич']
EMAIL_DOMAINS = ['gmail.com', 'yandex.ru']

def generate_phone():
    return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"

def generate_email(first_name, last_name):
    domain = random.choice(EMAIL_DOMAINS)
    return f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{domain}"

def generate_birth_date():
    years_ago = random.randint(18, 70)
    days_ago = years_ago * 365 + random.randint(-180, 180)
    birth_date = datetime.now() - timedelta(days=days_ago)
    return birth_date.strftime('%Y-%m-%d')

def generate_address():
    streets = ['Ленина', 'Гагарина', 'Советская']
    return f"г. Москва, ул. {random.choice(streets)}, д. {random.randint(1, 100)}, кв. {random.randint(1, 200)}"

def generate_unique_username(last_name, first_name, used_usernames):
    base_username = f"{last_name.lower()}_{first_name.lower()[0]}"
    username = base_username
    counter = 1
    while username in used_usernames:
        username = f"{base_username}{counter}"
        counter += 1
    used_usernames.add(username)
    return username

def create_tables(conn):
    print("🛠️ Создаём таблицы в БД...")
    cursor = conn.cursor()

    # Таблица клиентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            patronymic TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            date_of_birth DATE NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица логинов и паролей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_login (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL UNIQUE,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
        )
    ''')

    # Таблица счетов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            type_id INTEGER DEFAULT 1,
            balance REAL DEFAULT 0.0,
            currency TEXT DEFAULT 'RUB',
            status TEXT DEFAULT 'active',
            opened_by TEXT DEFAULT 'system',
            opened_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_date TIMESTAMP,
            interest_rate REAL DEFAULT 0.0,
            FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
        )
    ''')

    # Таблица транзакций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account_transaction (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES account(account_id) ON DELETE CASCADE
        )
    ''')

    # Таблица кредитов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            remaining_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
        )
    ''')

    # Таблица депозитов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposit (
            deposit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            startdate DATE NOT NULL,
            enddate DATE NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (client_id) REFERENCES client(client_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    print("✓ Все таблицы созданы успешно")

def populate_database(db_path="Bank_DB.db"):
    try:
        print(f"💾 Подключаемся к БД: {db_path}")
        conn = sqlite3.connect(db_path)

        print("Создаём таблицы...")
        create_tables(conn)

        cursor = conn.cursor()
        used_usernames = set()
        client_ids = []
        account_ids = []  # Храним ID счетов для создания транзакций

        print("👥 Создаём тестовых клиентов...")
        for i in range(3):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            patronymic = random.choice(PATRONYMICS)

            client_data = {
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic,
                'phone': generate_phone(),
                'email': generate_email(first_name, last_name),
                'address': generate_address(),
                'date_of_birth': generate_birth_date()
            }

            try:
                cursor.execute('''
                    INSERT INTO client (last_name, first_name, patronymic, phone, email, address, date_of_birth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
                    client_data['last_name'],
            client_data['first_name'],
            client_data['patronymic'],
            client_data['phone'],
            client_data['email'],
            client_data['address'],
            client_data['date_of_birth']
        ))
                client_id = cursor.lastrowid
                client_ids.append(client_id)
                print(f"✓ Клиент создан: {last_name} {first_name} (ID: {client_id})")

                # Создание логина
                username = generate_unique_username(last_name, first_name, used_usernames)
                password_hash = hashlib.sha256("password123".encode()).hexdigest()
                cursor.execute('''
            INSERT INTO user_login (client_id, username, password_hash)
            VALUES (?, ?, ?)
        ''', (client_id, username, password_hash))
                print(f"  ✓ Логин создан: {username}")


                # Создание счёта
                account_number = f"ACC-{random.randint(100000, 999999)}"
                balance = round(random.uniform(10000, 50000), 2)
                cursor.execute('''
            INSERT INTO account (client_id, account_number, balance)
            VALUES (?, ?, ?)
        ''', (client_id, account_number, balance))
                account_id = cursor.lastrowid
                account_ids.append(account_id)
                print(f"  ✓ Счёт создан: {account_number} (баланс: {balance} руб.)")

            except Exception as e:
                print(f"✗ Ошибка при создании клиента {last_name} {first_name}: {e}")
                conn.rollback()
                continue

        # Создаём транзакции для счетов
        print("\nСоздаём тестовые транзакции...")
        for account_id in account_ids:
            num_transactions = random.randint(2, 5)
            for _ in range(num_transactions):
                transaction_type = random.choice(['deposit', 'withdrawal'])
                amount = round(random.uniform(500, 15000), 2)
                description = f"Тестовая {transaction_type} на счёт {account_id}"

                try:
                    cursor.execute('''
                INSERT INTO account_transaction (account_id, transaction_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (account_id, transaction_type, amount, description))
                    print(f"  ✓ Транзакция: {transaction_type}, {amount} руб. для счёта ID: {account_id}")
                except Exception as e:
                    print(f"✗ Ошибка при создании транзакции для счёта {account_id}: {e}")
            conn.rollback()

        # Создаём кредиты для случайных клиентов
        print("\nСоздаём тестовые кредиты...")
        for _ in range(3):  # 3 кредита
            client_id = random.choice(client_ids)
            amount = round(random.uniform(50000, 200000), 2)
            remaining_amount = amount
            interest_rate = round(random.uniform(8, 15), 2)

            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d')

            try:
                cursor.execute('''
            INSERT INTO loan (
                client_id, amount, remaining_amount, interest_rate, start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (client_id, amount, remaining_amount, interest_rate, start_date, end_date))
                loan_id = cursor.lastrowid
                print(f"✓ Кредит ID: {loan_id} для клиента ID: {client_id} (сумма: {amount} руб., ставка: {interest_rate}%)")
            except Exception as e:
                print(f"✗ Ошибка при создании кредита для клиента {client_id}: {e}")
                conn.rollback()

        # Создаём депозиты для случайных клиентов
        print("\nСоздаём тестовые депозиты...")
        for _ in range(3):  # 3 депозита
            client_id = random.choice(client_ids)
            amount = round(random.uniform(30000, 150000), 2)
            interest_rate = round(random.uniform(4, 8), 2)

            startdate = datetime.now().strftime('%Y-%m-%d')
            enddate = (datetime.now() + timedelta(days=random.randint(180, 730))).strftime('%Y-%m-%d')

            try:
                cursor.execute('''
            INSERT INTO deposit (
                client_id, amount, interest_rate, startdate, enddate
            ) VALUES (?, ?, ?, ?, ?)
        ''', (client_id, amount, interest_rate, startdate, enddate))
                deposit_id = cursor.lastrowid
                print(f"✓ Депозит ID: {deposit_id} для клиента ID: {client_id} (сумма: {amount} руб., ставка: {interest_rate}%)")
            except Exception as e:
                print(f"✗ Ошибка при создании депозита для клиента {client_id}: {e}")
                conn.rollback()

        conn.commit()
        print(f"\n✅ База данных полностью заполнена! Создано {len(client_ids)} клиентов.")

    except Exception as e:
        print(f"✗ Критическая ошибка: {e}")
    finally:
        if conn:
            conn.close()
            print("🔒 Соединение с БД закрыто.")

# Вызов функции для запуска инициализации БД
if __name__ == "__main__":
    populate_database()
