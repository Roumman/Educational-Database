"""
Главный модуль запуска SQL‑тренажёра для банковской системы.


Оркестрирует взаимодействие трёх ключевых компонентов приложения:
* BankDatabase — работа с учебной базой данных банковской системы (Bank_DB);
* AuthManager — управление аутентификацией и авторизацией пользователей;
* BankUI — графический пользовательский интерфейс (GUI).
"""



from bank_db import BankDatabase
from auth import AuthManager
from ui import BankUI

def main():
    # Инициализация компонентов
    bank_db = BankDatabase("Bank_DB.db")
    auth_manager = AuthManager(bank_db)
    ui = BankUI(bank_db, auth_manager)

    # Запуск приложения
    ui.run()

if __name__ == "__main__":
    main()
