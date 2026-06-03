"""
Запуск графического интерфейса тренажёра.

Использует tkinter для отображения UI и класс TrainerUI из модуля trainer_ui.
При запуске создаёт экземпляр интерфейса и запускает главный цикл приложения.
"""



import tkinter as tk
from trainer_ui import TrainerUI

def main():
    # Создаём и запускаем интерфейс тренажёра
    app = TrainerUI()
    app.run()

if __name__ == "__main__":
    main()