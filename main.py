# main.py
# Точка входа в приложение.

import tkinter as tk
from gui import ReportApp


def main():
    """Главная функция запуска приложения."""
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()