# main.py
# Точка входа в приложение.

import tkinter as tk
from gui import ReportApp
from database import ensure_database_initialized


def main():
    """Главная функция запуска приложения."""
    # Инициализируем БД при первом запуске
    ensure_database_initialized()

    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()