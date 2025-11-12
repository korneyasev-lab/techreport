# question_type_dialog.py
# Диалог выбора типа вопроса с живыми примерами

import tkinter as tk
from tkinter import ttk
import configgui
import config


class QuestionTypeDialog:
    """Диалоговое окно для выбора типа вопроса с живыми примерами."""

    def __init__(self, parent, current_type="text_small", current_label="", current_items=None):
        self.parent = parent
        self.result = None  # Результат: тип вопроса

        # Текущие значения
        self.selected_type = tk.StringVar(value=current_type)
        self.question_label = current_label
        self.question_items = current_items or []

        # Создаём модальное окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Выбор типа вопроса")
        self.dialog.geometry("1200x800")
        self.dialog.configure(bg=configgui.COLORS["bg"])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Настройки шрифтов
        fonts, padding = configgui.get_settings()
        self.FONT_TITLE = ("Arial", 18, "bold")
        self.FONT_LARGE = ("Arial", 16)
        self.FONT_MEDIUM = ("Arial", 14)
        self.FONT_SMALL = ("Arial", 12)

        self.create_ui()

        # Центрируем окно
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)
        self.dialog.geometry(f"1200x800+{x}+{y}")

    def create_ui(self):
        """Создаёт интерфейс диалога."""
        # Заголовок
        tk.Label(
            self.dialog,
            text="ВЫБОР ТИПА ВОПРОСА",
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["title_bg"]
        ).pack(fill=tk.X, pady=15, ipady=10)

        # Основной контейнер с двумя панелями
        main_frame = tk.Frame(self.dialog, bg=configgui.COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: ВЫБОР ТИПА ==========
        left_frame = tk.LabelFrame(
            main_frame,
            text="ВЫБЕРИТЕ ТИП:",
            font=self.FONT_LARGE,
            padx=20,
            pady=20,
            bg=configgui.COLORS["bg"],
            fg=configgui.COLORS["label_fg"]
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Типы вопросов с описаниями
        types_info = [
            ("checkbox_group", "Группа чекбоксов", "Можно выбрать несколько\nвариантов"),
            ("checkbox_group_with_text", "Чекбоксы + текст", "Галочки + поле 'Другое'"),
            ("text_large", "Большое текстовое поле", "Много строк (3-5)\nдля подробного описания"),
            ("text_medium", "Среднее поле", "2-3 строки для комментария"),
            ("text_small", "Маленькое поле", "Одна строка\nдля короткого ответа"),
            ("yes_no", "Да/Нет", "Только один вариант")
        ]

        for i, (type_key, label, description) in enumerate(types_info):
            rb_frame = tk.Frame(left_frame, bg=configgui.COLORS["bg"])
            rb_frame.pack(fill=tk.X, pady=8)

            rb = tk.Radiobutton(
                rb_frame,
                text=label,
                variable=self.selected_type,
                value=type_key,
                font=self.FONT_LARGE,
                command=self.update_preview
            )
            rb.pack(anchor='w')

            tk.Label(
                rb_frame,
                text=description,
                font=self.FONT_SMALL,
                fg="gray",
                bg=configgui.COLORS["bg"],
                justify=tk.LEFT
            ).pack(anchor='w', padx=25)

        # ========== ПРАВАЯ ПАНЕЛЬ: ЖИВОЙ ПРИМЕР ==========
        right_frame = tk.LabelFrame(
            main_frame,
            text="ПОПРОБУЙТЕ (как будет в отчёте):",
            font=self.FONT_LARGE,
            padx=20,
            pady=20,
            bg=configgui.COLORS["bg"],
            fg=configgui.COLORS["label_fg"]
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Контейнер для примера
        self.preview_frame = tk.Frame(right_frame, bg=configgui.COLORS["bg"])
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

        # Настройка весов grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Показываем первый пример
        self.update_preview()

        # ========== НИЖНЯЯ ПАНЕЛЬ: КНОПКИ ==========
        bottom_frame = tk.Frame(self.dialog, bg=configgui.COLORS["bg"])
        bottom_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(
            bottom_frame,
            text="✓ Выбрать",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.on_select,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            bottom_frame,
            text="✗ Отмена",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.on_cancel,
            width=15,
            height=2
        ).pack(side=tk.RIGHT, padx=10)

    def update_preview(self):
        """Обновляет живой пример справа при выборе типа."""
        # Очищаем контейнер
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        question_type = self.selected_type.get()

        # Заголовок примера
        example_label = self.question_label or "Пример вопроса:"
        tk.Label(
            self.preview_frame,
            text=example_label,
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            anchor='w'
        ).pack(fill=tk.X, pady=10)

        # Рисуем пример в зависимости от типа
        if question_type == "checkbox_group":
            self.show_checkbox_example()

        elif question_type == "checkbox_group_with_text":
            self.show_checkbox_with_text_example()

        elif question_type == "text_large":
            self.show_text_large_example()

        elif question_type == "text_medium":
            self.show_text_medium_example()

        elif question_type == "text_small":
            self.show_text_small_example()

        elif question_type == "yes_no":
            self.show_yes_no_example()

    def show_checkbox_example(self):
        """Показывает пример группы чекбоксов."""
        items = self.question_items if self.question_items else [
            "Отклонения по цвету",
            "Растекаемость ниже нормы",
            "Вода выше нормы",
            "Другие отклонения"
        ]

        for item in items:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.preview_frame,
                text=item,
                variable=var,
                font=self.FONT_MEDIUM
            )
            cb.pack(anchor='w', pady=3)

    def show_checkbox_with_text_example(self):
        """Показывает пример чекбоксов + текстовое поле."""
        items = self.question_items if self.question_items else [
            "Подогрев воды",
            "Лимонная кислота"
        ]

        for item in items:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(
                self.preview_frame,
                text=item,
                variable=var,
                font=self.FONT_MEDIUM
            )
            cb.pack(anchor='w', pady=3)

        tk.Label(
            self.preview_frame,
            text="Другое:",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"]
        ).pack(anchor='w', pady=(10, 3))

        tk.Entry(
            self.preview_frame,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            width=40
        ).pack(anchor='w', pady=3)

    def show_text_large_example(self):
        """Показывает пример большого текстового поля."""
        text_widget = tk.Text(
            self.preview_frame,
            height=5,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        text_widget.insert("1.0", "Введите подробный комментарий...\n\nМожно писать много строк\nдля детального описания.")

    def show_text_medium_example(self):
        """Показывает пример среднего текстового поля."""
        text_widget = tk.Text(
            self.preview_frame,
            height=3,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.X, pady=5)
        text_widget.insert("1.0", "Краткий комментарий (2-3 строки)...")

    def show_text_small_example(self):
        """Показывает пример маленького поля."""
        entry = tk.Entry(
            self.preview_frame,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            width=30
        )
        entry.pack(anchor='w', pady=5)
        entry.insert(0, "18-24°C")

    def show_yes_no_example(self):
        """Показывает пример выбора Да/Нет."""
        var = tk.StringVar(value="Да")

        rb_frame = tk.Frame(self.preview_frame)
        rb_frame.pack(anchor='w', pady=10)

        tk.Radiobutton(
            rb_frame,
            text="Да",
            variable=var,
            value="Да",
            font=self.FONT_MEDIUM
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            rb_frame,
            text="Нет",
            variable=var,
            value="Нет",
            font=self.FONT_MEDIUM
        ).pack(side=tk.LEFT, padx=10)

    def on_select(self):
        """Обработчик кнопки Выбрать."""
        self.result = self.selected_type.get()
        self.dialog.destroy()

    def on_cancel(self):
        """Обработчик кнопки Отмена."""
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Показывает диалог и возвращает выбранный тип."""
        self.dialog.wait_window()
        return self.result
