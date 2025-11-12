# question_editor_full.py
# Полноценный редактор вопроса в отдельном окне

import tkinter as tk
from tkinter import messagebox
import configgui
from database import ConfigDatabase
import config


class QuestionEditorDialog:
    """Полноценный редактор вопроса в отдельном модальном окне."""

    def __init__(self, parent, question_id, db):
        self.parent = parent
        self.question_id = question_id
        self.db = db
        self.result = False  # Успешно сохранено или нет

        # Загружаем данные вопроса
        self.load_question_data()

        # Создаём модальное окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактор вопроса")

        # Получаем размер экрана
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Размер окна - 90% экрана, но не больше 1400x750
        width = min(int(screen_width * 0.9), 1400)
        height = min(int(screen_height * 0.85), 750)

        self.dialog.geometry(f"{width}x{height}")
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
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def load_question_data(self):
        """Загружает данные вопроса из БД."""
        # Получаем вопрос
        questions = self.db.get_questions_by_block(self.question_id)

        # Ищем нужный вопрос
        self.db.connect()
        self.db.cursor.execute('SELECT * FROM questions WHERE id = ?', (self.question_id,))
        row = self.db.cursor.fetchone()
        self.db.close()

        if row:
            self.question_type = row['question_type']
            self.question_label = row['label']
            self.question_height = row['height']
            self.question_placeholder = row['placeholder']
        else:
            self.question_type = "text_small"
            self.question_label = ""
            self.question_height = None
            self.question_placeholder = None

        # Загружаем варианты ответов
        self.question_options = self.db.get_question_options(self.question_id)
        self.options_list = [opt['option_text'] for opt in self.question_options]

        # Переменная для выбранного типа
        self.selected_type = tk.StringVar(value=self.question_type)

    def create_ui(self):
        """Создаёт интерфейс редактора."""
        # Заголовок
        tk.Label(
            self.dialog,
            text="✏️ РЕДАКТОР ВОПРОСА",
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=10)

        # Верхняя часть: выбор типа и пример
        top_frame = tk.Frame(self.dialog)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: ВЫБОР ТИПА ==========
        left_frame = tk.LabelFrame(
            top_frame,
            text="ВЫБЕРИТЕ ТИП (16 шрифт):",
            font=self.FONT_LARGE,
            padx=20,
            pady=20
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
            rb_frame = tk.Frame(left_frame)
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
                justify=tk.LEFT
            ).pack(anchor='w', padx=25)

        # ========== ПРАВАЯ ПАНЕЛЬ: ЖИВОЙ ПРИМЕР ==========
        right_frame = tk.LabelFrame(
            top_frame,
            text="ПОПРОБУЙТЕ (как будет в отчёте):",
            font=self.FONT_LARGE,
            padx=20,
            pady=20
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Контейнер для примера
        self.preview_frame = tk.Frame(right_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)

        # Настройка весов grid
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=2)
        top_frame.rowconfigure(0, weight=1)

        # ========== НИЖНЯЯ ЧАСТЬ: РЕДАКТИРОВАНИЕ ==========
        bottom_frame = tk.LabelFrame(
            self.dialog,
            text="Настройки вопроса:",
            font=self.FONT_LARGE,
            padx=20,
            pady=15
        )
        bottom_frame.pack(fill=tk.BOTH, padx=20, pady=10)

        # Текст вопроса
        tk.Label(
            bottom_frame,
            text="Текст вопроса (14 шрифт):",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            anchor='w'
        ).pack(fill=tk.X, pady=5)

        self.label_text = tk.Text(
            bottom_frame,
            height=2,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            wrap=tk.WORD
        )
        self.label_text.pack(fill=tk.X, pady=5)
        self.label_text.insert("1.0", self.question_label)

        # Варианты ответов (показываем только для чекбоксов)
        self.options_container = tk.Frame(bottom_frame)
        self.options_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.show_options_editor()

        # ========== КНОПКИ ==========
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Button(
            btn_frame,
            text="💾 Сохранить",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.save_question,
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="❌ Отмена",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.cancel,
            width=15,
            height=2
        ).pack(side=tk.RIGHT, padx=10)

        # Показываем первый пример
        self.update_preview()

    def show_options_editor(self):
        """Показывает редактор вариантов ответов."""
        for widget in self.options_container.winfo_children():
            widget.destroy()

        question_type = self.selected_type.get()

        if 'checkbox' in question_type:
            tk.Label(
                self.options_container,
                text="Варианты ответов (только для чекбоксов):",
                font=self.FONT_MEDIUM,
                fg=configgui.COLORS["label_fg"],
                anchor='w'
            ).pack(fill=tk.X, pady=5)

            # Список вариантов
            self.options_listbox = tk.Listbox(
                self.options_container,
                font=self.FONT_MEDIUM,
                height=5,
                bg=configgui.COLORS["text_bg"],
                fg=configgui.COLORS["text_fg"]
            )
            self.options_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

            for option in self.options_list:
                self.options_listbox.insert(tk.END, f"• {option}")

            # Кнопки управления вариантами
            btn_frame = tk.Frame(self.options_container)
            btn_frame.pack(fill=tk.X, pady=5)

            self.new_option_entry = tk.Entry(
                btn_frame,
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["text_bg"],
                fg=configgui.COLORS["text_fg"]
            )
            self.new_option_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

            tk.Button(
                btn_frame,
                text="➕ Добавить",
                font=self.FONT_SMALL,
                command=self.add_option,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            ).pack(side=tk.LEFT, padx=2)

            tk.Button(
                btn_frame,
                text="🗑️ Удалить выбранный",
                font=self.FONT_SMALL,
                command=self.delete_option,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            ).pack(side=tk.LEFT, padx=2)

    def add_option(self):
        """Добавляет новый вариант ответа."""
        new_text = self.new_option_entry.get().strip()
        if new_text:
            self.options_list.append(new_text)
            self.options_listbox.insert(tk.END, f"• {new_text}")
            self.new_option_entry.delete(0, tk.END)
            self.update_preview()

    def delete_option(self):
        """Удаляет выбранный вариант."""
        selection = self.options_listbox.curselection()
        if selection:
            index = selection[0]
            self.options_list.pop(index)
            self.options_listbox.delete(index)
            self.update_preview()

    def update_preview(self):
        """Обновляет живой пример справа."""
        # Очищаем контейнер
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # Обновляем редактор вариантов при смене типа
        self.show_options_editor()

        question_type = self.selected_type.get()
        label = self.label_text.get("1.0", tk.END).strip() or "Пример вопроса:"

        # Заголовок примера
        tk.Label(
            self.preview_frame,
            text=label,
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
        # Используем реальные варианты из списка ниже
        if not self.options_list:
            tk.Label(
                self.preview_frame,
                text="⚠ Добавьте варианты ответов внизу",
                font=self.FONT_SMALL,
                fg="orange"
            ).pack(pady=20)
            return

        for item in self.options_list:
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
        # Используем реальные варианты
        if not self.options_list:
            tk.Label(
                self.preview_frame,
                text="⚠ Добавьте варианты ответов внизу",
                font=self.FONT_SMALL,
                fg="orange"
            ).pack(pady=10)
        else:
            for item in self.options_list:
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
        text_widget.insert("1.0", "Введите подробный комментарий...\n\nМожно писать много строк.")

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

    def save_question(self):
        """Сохраняет изменения вопроса в БД."""
        new_label = self.label_text.get("1.0", tk.END).strip()
        new_type = self.selected_type.get()

        if not new_label:
            messagebox.showwarning("Ошибка", "Введите текст вопроса!", parent=self.dialog)
            return

        # Сохраняем вопрос
        self.db.update_question(
            self.question_id,
            new_label,
            new_type,
            self.question_height,
            self.question_placeholder
        )

        # Если тип чекбоксы - обновляем варианты
        if 'checkbox' in new_type:
            # Удаляем старые варианты
            for opt in self.question_options:
                self.db.delete_option(opt['id'])

            # Добавляем новые
            for option_text in self.options_list:
                self.db.add_option(self.question_id, option_text)

        self.result = True
        messagebox.showinfo("Успех", "Вопрос сохранён!", parent=self.dialog)
        self.dialog.destroy()

    def cancel(self):
        """Закрывает окно без сохранения."""
        self.result = False
        self.dialog.destroy()

    def show(self):
        """Показывает диалог и возвращает результат."""
        self.dialog.wait_window()
        return self.result
