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
        self.dialog.configure(bg=configgui.COLORS["bg"])

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
        # Заголовок с кнопками
        header_frame = tk.Frame(self.dialog, bg=configgui.COLORS["title_bg"])
        header_frame.pack(fill=tk.X, pady=0)

        tk.Label(
            header_frame,
            text="✏️ РЕДАКТОР ВОПРОСА",
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["title_bg"]
        ).pack(side=tk.LEFT, padx=20, pady=10)

        # Кнопки справа
        buttons_right = tk.Frame(header_frame, bg=configgui.COLORS["title_bg"])
        buttons_right.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Button(
            buttons_right,
            text="💾 Сохранить",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.save_question,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            buttons_right,
            text="❌ Отмена",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.cancel,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # Верхняя часть: выбор типа и редактирование
        top_frame = tk.Frame(self.dialog, bg=configgui.COLORS["bg"])
        top_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: ВЫБОР ТИПА (только 2!) ==========
        left_frame = tk.LabelFrame(
            top_frame,
            text="ВЫБЕРИТЕ ТИП:",
            font=self.FONT_LARGE,
            padx=20,
            pady=20,
            bg=configgui.COLORS["bg"],
            fg=configgui.COLORS["label_fg"]
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        # Только 2 типа: Чекбоксы и Текстовое поле
        types_info = [
            ("checkbox_group", "Чекбоксы", "Можно выбрать несколько\n(2-8 вариантов)"),
            ("text", "Текстовое поле", "Малое/Среднее/Большое")
        ]

        for i, (type_key, label, description) in enumerate(types_info):
            rb_frame = tk.Frame(left_frame, bg=configgui.COLORS["bg"])
            rb_frame.pack(fill=tk.X, pady=15)

            rb = tk.Radiobutton(
                rb_frame,
                text=label,
                variable=self.selected_type,
                value=type_key,
                font=self.FONT_LARGE,
                command=self.update_editor
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

        # ========== ПРАВАЯ ПАНЕЛЬ: РЕДАКТИРОВАНИЕ ==========
        right_frame = tk.LabelFrame(
            top_frame,
            text="РЕДАКТИРОВАНИЕ:",
            font=self.FONT_LARGE,
            padx=20,
            pady=10,
            bg=configgui.COLORS["bg"],
            fg=configgui.COLORS["label_fg"]
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Кнопка Редактировать вверху
        tk.Button(
            right_frame,
            text="✏️ Редактировать",
            font=self.FONT_LARGE,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            width=20,
            height=1
        ).pack(pady=10)

        # Текст вопроса
        tk.Label(
            right_frame,
            text="Текст вопроса:",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"],
            anchor='w'
        ).pack(fill=tk.X, pady=(10, 5))

        self.label_text = tk.Text(
            right_frame,
            height=2,
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"],
            wrap=tk.WORD
        )
        self.label_text.pack(fill=tk.X, pady=5)
        self.label_text.insert("1.0", self.question_label)

        # Контейнер для специфичных настроек (чекбоксы или размер текста)
        self.editor_container = tk.Frame(right_frame, bg=configgui.COLORS["bg"])
        self.editor_container.pack(fill=tk.BOTH, expand=True, pady=10)

        # Настройка весов grid
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=2)
        top_frame.rowconfigure(0, weight=1)

        # Показываем редактор для выбранного типа
        self.update_editor()

    def update_editor(self):
        """Обновляет редактор в правой панели в зависимости от типа."""
        # Очищаем контейнер
        for widget in self.editor_container.winfo_children():
            widget.destroy()

        question_type = self.selected_type.get()

        if question_type == "checkbox_group":
            self.show_checkbox_editor()
        elif question_type == "text":
            self.show_text_size_editor()

    def show_checkbox_editor(self):
        """Показывает редактор вариантов для чекбоксов."""
        tk.Label(
            self.editor_container,
            text="Варианты ответов (2-8 вариантов):",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"],
            anchor='w'
        ).pack(fill=tk.X, pady=5)

        # Список вариантов
        self.options_listbox = tk.Listbox(
            self.editor_container,
            font=self.FONT_MEDIUM,
            height=6,
            bg=configgui.COLORS["bg"],
            fg=configgui.COLORS["label_fg"],
            selectbackground=configgui.COLORS["button_bg"],
            selectforeground=configgui.COLORS["label_fg"],
            highlightthickness=1,
            highlightbackground=configgui.COLORS["button_bg"]
        )
        self.options_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        for option in self.options_list:
            self.options_listbox.insert(tk.END, f"• {option}")

        # Кнопки управления вариантами
        btn_frame = tk.Frame(self.editor_container, bg=configgui.COLORS["bg"])
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
            text="🗑️ Удалить",
            font=self.FONT_SMALL,
            command=self.delete_option,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(side=tk.LEFT, padx=2)

    def show_text_size_editor(self):
        """Показывает выбор размера текстового поля."""
        tk.Label(
            self.editor_container,
            text="Выберите размер поля:",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"],
            anchor='w'
        ).pack(fill=tk.X, pady=5)

        # Переменная для размера (если есть height в БД)
        if self.question_height:
            if self.question_height == 1:
                default_size = "small"
            elif self.question_height <= 3:
                default_size = "medium"
            else:
                default_size = "large"
        else:
            default_size = "medium"

        self.text_size_var = tk.StringVar(value=default_size)

        sizes = [
            ("small", "Малое (1 строка)", 1),
            ("medium", "Среднее (2-3 строки)", 3),
            ("large", "Большое (4-5 строк)", 5)
        ]

        for size_key, size_label, height in sizes:
            rb = tk.Radiobutton(
                self.editor_container,
                text=size_label,
                variable=self.text_size_var,
                value=size_key,
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["bg"],
                fg=configgui.COLORS["label_fg"]
            )
            rb.pack(anchor='w', pady=5)

    def add_option(self):
        """Добавляет новый вариант ответа."""
        new_text = self.new_option_entry.get().strip()
        if new_text:
            self.options_list.append(new_text)
            self.options_listbox.insert(tk.END, f"• {new_text}")
            self.new_option_entry.delete(0, tk.END)

    def delete_option(self):
        """Удаляет выбранный вариант."""
        selection = self.options_listbox.curselection()
        if selection:
            index = selection[0]
            self.options_list.pop(index)
            self.options_listbox.delete(index)








    def save_question(self):
        """Сохраняет изменения вопроса в БД."""
        new_label = self.label_text.get("1.0", tk.END).strip()
        new_type = self.selected_type.get()

        if not new_label:
            messagebox.showwarning("Ошибка", "Введите текст вопроса!", parent=self.dialog)
            return

        # Определяем height и конкретный тип
        if new_type == "text":
            # Получаем размер из радиокнопок
            size = self.text_size_var.get()
            if size == "small":
                final_type = "text_small"
                height = 1
            elif size == "medium":
                final_type = "text_medium"
                height = 3
            else:  # large
                final_type = "text_large"
                height = 5
        elif new_type == "checkbox_group":
            final_type = "checkbox_group"
            height = None
            # Проверка: должно быть от 2 до 8 вариантов
            if len(self.options_list) < 2:
                messagebox.showwarning("Ошибка", "Добавьте минимум 2 варианта ответа!", parent=self.dialog)
                return
            if len(self.options_list) > 8:
                messagebox.showwarning("Ошибка", "Максимум 8 вариантов ответа!", parent=self.dialog)
                return
        else:
            final_type = new_type
            height = self.question_height

        # Сохраняем вопрос
        self.db.update_question(
            self.question_id,
            new_label,
            final_type,
            height,
            self.question_placeholder
        )

        # Если тип чекбоксы - обновляем варианты
        if new_type == "checkbox_group":
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
