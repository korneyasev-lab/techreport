# editor.py
# Графический редактор структуры отчётов

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import configgui
from database import ConfigDatabase
import config
from question_type_dialog import QuestionTypeDialog


class QuestionEditorWindow:
    """Окно редактора вопросов отчёта."""

    def __init__(self, parent):
        self.parent = parent
        self.db = ConfigDatabase()

        # Создаём отдельное окно
        self.window = tk.Toplevel(parent)
        self.window.title("Редактор структуры отчёта")
        self.window.geometry("1400x800")

        # Адаптация настроек
        fonts, padding = configgui.get_settings()
        self.FONT_TITLE = ("Arial", fonts["title"], "bold")
        self.FONT_MEDIUM = ("Arial", fonts["medium"])
        self.FONT_SMALL = ("Arial", fonts["small"])

        # Данные
        self.selected_block_id = None
        self.selected_question_id = None
        self.blocks = []
        self.questions = []

        self.create_ui()
        self.load_blocks()

    def create_ui(self):
        """Создаёт интерфейс редактора."""
        # Заголовок
        tk.Label(
            self.window,
            text="⚙️ РЕДАКТОР СТРУКТУРЫ ОТЧЁТА",
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=10)

        # Основной контейнер с тремя панелями
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: РАЗДЕЛЫ ==========
        left_frame = tk.LabelFrame(main_frame, text="📋 РАЗДЕЛЫ", font=self.FONT_MEDIUM, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        # Список разделов
        self.blocks_listbox = tk.Listbox(
            left_frame,
            font=self.FONT_SMALL,
            height=20,
            width=30,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"]
        )
        self.blocks_listbox.pack(fill=tk.BOTH, expand=True)
        self.blocks_listbox.bind('<<ListboxSelect>>', self.on_block_selected)

        # Кнопки управления разделами
        blocks_btn_frame = tk.Frame(left_frame)
        blocks_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            blocks_btn_frame,
            text="➕ Новый раздел",
            font=self.FONT_SMALL,
            command=self.add_block,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            blocks_btn_frame,
            text="✏️ Переименовать",
            font=self.FONT_SMALL,
            command=self.rename_block,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            blocks_btn_frame,
            text="🗑️ Удалить раздел",
            font=self.FONT_SMALL,
            command=self.delete_block,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=2)

        # ========== ЦЕНТРАЛЬНАЯ ПАНЕЛЬ: ВОПРОСЫ ==========
        center_frame = tk.LabelFrame(main_frame, text="❓ ВОПРОСЫ РАЗДЕЛА", font=self.FONT_MEDIUM, padx=10, pady=10)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5)

        # Список вопросов
        self.questions_listbox = tk.Listbox(
            center_frame,
            font=self.FONT_SMALL,
            height=20,
            width=40,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"]
        )
        self.questions_listbox.pack(fill=tk.BOTH, expand=True)
        self.questions_listbox.bind('<<ListboxSelect>>', self.on_question_selected)

        # Кнопки управления вопросами
        questions_btn_frame = tk.Frame(center_frame)
        questions_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            questions_btn_frame,
            text="➕ Добавить вопрос",
            font=self.FONT_SMALL,
            command=self.add_question,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            questions_btn_frame,
            text="🗑️ Удалить вопрос",
            font=self.FONT_SMALL,
            command=self.delete_question,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=2)

        move_frame = tk.Frame(questions_btn_frame)
        move_frame.pack(fill=tk.X, pady=2)

        tk.Button(
            move_frame,
            text="⬆️ Вверх",
            font=self.FONT_SMALL,
            command=self.move_question_up,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        tk.Button(
            move_frame,
            text="⬇️ Вниз",
            font=self.FONT_SMALL,
            command=self.move_question_down,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # ========== ПРАВАЯ ПАНЕЛЬ: РЕДАКТИРОВАНИЕ ВОПРОСА ==========
        right_frame = tk.LabelFrame(main_frame, text="✏️ РЕДАКТОР ВОПРОСА", font=self.FONT_MEDIUM, padx=10, pady=10)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=5)

        # Скроллируемая область
        canvas = tk.Canvas(right_frame, bg=configgui.COLORS["bg"])
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.editor_frame = tk.Frame(canvas, bg=configgui.COLORS["bg"])

        self.editor_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.editor_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Изначально пусто
        tk.Label(
            self.editor_frame,
            text="Выберите вопрос для редактирования",
            font=self.FONT_MEDIUM,
            fg="gray"
        ).pack(pady=50)

        # Настройка grid весов
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # ========== НИЖНЯЯ ПАНЕЛЬ: КНОПКИ ==========
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(
            bottom_frame,
            text="🔄 Сбросить к умолчаниям",
            font=self.FONT_MEDIUM,
            command=self.reset_to_defaults,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="❌ Закрыть",
            font=self.FONT_MEDIUM,
            command=self.window.destroy,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(side=tk.RIGHT, padx=5)

    # ============================================================
    # ЗАГРУЗКА ДАННЫХ
    # ============================================================

    def load_blocks(self):
        """Загружает список разделов из БД."""
        self.blocks_listbox.delete(0, tk.END)
        self.blocks = self.db.get_all_blocks()

        for block in self.blocks:
            self.blocks_listbox.insert(tk.END, block['title'])

        # Очистка вопросов и редактора
        self.questions_listbox.delete(0, tk.END)
        self.clear_editor()

    def load_questions(self, block_id):
        """Загружает список вопросов для выбранного раздела."""
        self.questions_listbox.delete(0, tk.END)
        self.questions = self.db.get_questions_by_block(block_id)

        for i, question in enumerate(self.questions):
            display_text = f"{i+1}. {question['label'][:50]}..."
            self.questions_listbox.insert(tk.END, display_text)

        self.clear_editor()

    def clear_editor(self):
        """Очищает панель редактирования вопроса."""
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.editor_frame,
            text="Выберите вопрос для редактирования",
            font=self.FONT_MEDIUM,
            fg="gray"
        ).pack(pady=50)

    def load_question_editor(self, question_id):
        """Загружает форму редактирования вопроса."""
        # Очистка
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        # Получаем данные вопроса
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if not question:
            return

        # Тип вопроса
        tk.Label(
            self.editor_frame,
            text="Тип вопроса:",
            font=self.FONT_MEDIUM,
            anchor='w'
        ).pack(fill=tk.X, pady=5)

        self.question_type_var = tk.StringVar(value=question['question_type'])

        # Рамка для отображения текущего типа и кнопки
        type_frame = tk.Frame(self.editor_frame)
        type_frame.pack(fill=tk.X, pady=5)

        # Отображение текущего типа
        type_name = config.ELEMENT_TYPES.get(question['question_type'], question['question_type'])
        self.type_label = tk.Label(
            type_frame,
            text=f"→ {type_name}",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            anchor='w'
        )
        self.type_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Кнопка выбора типа
        tk.Button(
            type_frame,
            text="⚙ Выбрать тип",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=lambda: self.open_type_dialog(question_id),
            width=15
        ).pack(side=tk.RIGHT, padx=5)

        # Текст вопроса
        tk.Label(
            self.editor_frame,
            text="Текст вопроса:",
            font=self.FONT_MEDIUM,
            anchor='w'
        ).pack(fill=tk.X, pady=5)

        self.question_label_text = tk.Text(
            self.editor_frame,
            height=3,
            font=self.FONT_SMALL,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"]
        )
        self.question_label_text.pack(fill=tk.X, pady=5)
        self.question_label_text.insert("1.0", question['label'])

        # Дополнительные поля для текстовых полей
        self.height_var = tk.StringVar(value=str(question['height'] or ''))
        self.placeholder_var = tk.StringVar(value=question['placeholder'] or '')

        if 'text' in question['question_type']:
            tk.Label(
                self.editor_frame,
                text="Высота поля (строк):",
                font=self.FONT_SMALL
            ).pack(fill=tk.X, pady=2)

            tk.Entry(
                self.editor_frame,
                textvariable=self.height_var,
                font=self.FONT_SMALL,
                bg=configgui.COLORS["text_bg"],
                fg=configgui.COLORS["text_fg"]
            ).pack(fill=tk.X, pady=2)

            tk.Label(
                self.editor_frame,
                text="Placeholder (подсказка):",
                font=self.FONT_SMALL
            ).pack(fill=tk.X, pady=2)

            tk.Entry(
                self.editor_frame,
                textvariable=self.placeholder_var,
                font=self.FONT_SMALL,
                bg=configgui.COLORS["text_bg"],
                fg=configgui.COLORS["text_fg"]
            ).pack(fill=tk.X, pady=2)

        # Варианты ответов (для чекбоксов)
        if 'checkbox' in question['question_type']:
            tk.Label(
                self.editor_frame,
                text="Варианты ответов:",
                font=self.FONT_MEDIUM,
                anchor='w'
            ).pack(fill=tk.X, pady=10)

            # Список вариантов
            self.options_frame = tk.Frame(self.editor_frame)
            self.options_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            self.load_options(question_id)

            # Добавление нового варианта
            add_option_frame = tk.Frame(self.editor_frame)
            add_option_frame.pack(fill=tk.X, pady=5)

            self.new_option_var = tk.StringVar()
            tk.Entry(
                add_option_frame,
                textvariable=self.new_option_var,
                font=self.FONT_SMALL,
                bg=configgui.COLORS["text_bg"],
                fg=configgui.COLORS["text_fg"]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

            tk.Button(
                add_option_frame,
                text="➕ Добавить вариант",
                font=self.FONT_SMALL,
                command=lambda: self.add_option(question_id),
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            ).pack(side=tk.LEFT)

        # Кнопка сохранения
        tk.Button(
            self.editor_frame,
            text="💾 Сохранить вопрос",
            font=self.FONT_MEDIUM,
            command=lambda: self.save_question(question_id),
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"]
        ).pack(fill=tk.X, pady=20)

    def load_options(self, question_id):
        """Загружает список вариантов ответов."""
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        options = self.db.get_question_options(question_id)

        for option in options:
            option_row = tk.Frame(self.options_frame)
            option_row.pack(fill=tk.X, pady=2)

            tk.Label(
                option_row,
                text=f"☑ {option['option_text']}",
                font=self.FONT_SMALL,
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Button(
                option_row,
                text="🗑️",
                font=self.FONT_SMALL,
                command=lambda opt_id=option['id']: self.delete_option(opt_id, question_id),
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            ).pack(side=tk.RIGHT)

    # ============================================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # ============================================================

    def on_block_selected(self, event):
        """Обработчик выбора раздела."""
        selection = self.blocks_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_block_id = self.blocks[index]['id']
            self.load_questions(self.selected_block_id)

    def on_question_selected(self, event):
        """Обработчик выбора вопроса."""
        selection = self.questions_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_question_id = self.questions[index]['id']
            self.load_question_editor(self.selected_question_id)

    def open_type_dialog(self, question_id):
        """Открывает диалог выбора типа вопроса."""
        # Получаем текущие данные вопроса
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if not question:
            return

        # Получаем варианты ответов для примера
        options = self.db.get_question_options(question_id)
        items = [opt['option_text'] for opt in options] if options else []

        # Открываем диалог
        dialog = QuestionTypeDialog(
            self.window,
            current_type=question['question_type'],
            current_label=question['label'],
            current_items=items
        )
        new_type = dialog.show()

        # Если пользователь выбрал новый тип
        if new_type and new_type != question['question_type']:
            self.question_type_var.set(new_type)
            # Обновляем отображение типа
            type_name = config.ELEMENT_TYPES.get(new_type, new_type)
            self.type_label.config(text=f"→ {type_name}")
            messagebox.showinfo(
                "Тип изменён",
                f"Тип вопроса изменён на: {type_name}\n\nНе забудьте сохранить вопрос!",
                parent=self.window
            )

    # ============================================================
    # ДЕЙСТВИЯ С РАЗДЕЛАМИ
    # ============================================================

    def add_block(self):
        """Добавляет новый раздел."""
        title = simpledialog.askstring("Новый раздел", "Введите название раздела:", parent=self.window)
        if title:
            self.db.add_block(title)
            self.load_blocks()
            messagebox.showinfo("Успех", "Раздел добавлен!", parent=self.window)

    def rename_block(self):
        """Переименовывает выбранный раздел."""
        if not self.selected_block_id:
            messagebox.showwarning("Ошибка", "Выберите раздел!", parent=self.window)
            return

        block = next((b for b in self.blocks if b['id'] == self.selected_block_id), None)
        if not block:
            return

        new_title = simpledialog.askstring(
            "Переименовать",
            "Введите новое название:",
            initialvalue=block['title'],
            parent=self.window
        )

        if new_title:
            self.db.update_block_title(self.selected_block_id, new_title)
            self.load_blocks()
            messagebox.showinfo("Успех", "Раздел переименован!", parent=self.window)

    def delete_block(self):
        """Удаляет выбранный раздел."""
        if not self.selected_block_id:
            messagebox.showwarning("Ошибка", "Выберите раздел!", parent=self.window)
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            "Удалить раздел и все его вопросы?",
            parent=self.window
        )

        if confirm:
            self.db.delete_block(self.selected_block_id)
            self.selected_block_id = None
            self.load_blocks()
            messagebox.showinfo("Успех", "Раздел удалён!", parent=self.window)

    # ============================================================
    # ДЕЙСТВИЯ С ВОПРОСАМИ
    # ============================================================

    def add_question(self):
        """Добавляет новый вопрос."""
        if not self.selected_block_id:
            messagebox.showwarning("Ошибка", "Сначала выберите раздел!", parent=self.window)
            return

        label = simpledialog.askstring("Новый вопрос", "Введите текст вопроса:", parent=self.window)
        if label:
            self.db.add_question(self.selected_block_id, "text_small", label)
            self.load_questions(self.selected_block_id)
            messagebox.showinfo("Успех", "Вопрос добавлен!", parent=self.window)

    def delete_question(self):
        """Удаляет выбранный вопрос."""
        if not self.selected_question_id:
            messagebox.showwarning("Ошибка", "Выберите вопрос!", parent=self.window)
            return

        confirm = messagebox.askyesno("Подтверждение", "Удалить вопрос?", parent=self.window)

        if confirm:
            self.db.delete_question(self.selected_question_id)
            self.selected_question_id = None
            self.load_questions(self.selected_block_id)
            messagebox.showinfo("Успех", "Вопрос удалён!", parent=self.window)

    def move_question_up(self):
        """Перемещает вопрос вверх."""
        if not self.selected_question_id:
            messagebox.showwarning("Ошибка", "Выберите вопрос!", parent=self.window)
            return

        self.db.move_question_up(self.selected_question_id)
        self.load_questions(self.selected_block_id)

    def move_question_down(self):
        """Перемещает вопрос вниз."""
        if not self.selected_question_id:
            messagebox.showwarning("Ошибка", "Выберите вопрос!", parent=self.window)
            return

        self.db.move_question_down(self.selected_question_id)
        self.load_questions(self.selected_block_id)

    def save_question(self, question_id):
        """Сохраняет изменения вопроса."""
        label = self.question_label_text.get("1.0", tk.END).strip()
        question_type = self.question_type_var.get()

        height = None
        if self.height_var.get():
            try:
                height = int(self.height_var.get())
            except ValueError:
                pass

        placeholder = self.placeholder_var.get() if self.placeholder_var.get() else None

        self.db.update_question(question_id, label, question_type, height, placeholder)
        self.load_questions(self.selected_block_id)
        messagebox.showinfo("Успех", "Вопрос сохранён!", parent=self.window)

    # ============================================================
    # ДЕЙСТВИЯ С ВАРИАНТАМИ ОТВЕТОВ
    # ============================================================

    def add_option(self, question_id):
        """Добавляет новый вариант ответа."""
        option_text = self.new_option_var.get().strip()
        if option_text:
            self.db.add_option(question_id, option_text)
            self.new_option_var.set('')
            self.load_options(question_id)

    def delete_option(self, option_id, question_id):
        """Удаляет вариант ответа."""
        self.db.delete_option(option_id)
        self.load_options(question_id)

    # ============================================================
    # СБРОС К УМОЛЧАНИЯМ
    # ============================================================

    def reset_to_defaults(self):
        """Сбрасывает конфигурацию к настройкам по умолчанию."""
        confirm = messagebox.askyesno(
            "Подтверждение",
            "Сбросить всю структуру отчёта к настройкам по умолчанию?\nВсе изменения будут потеряны!",
            parent=self.window
        )

        if confirm:
            self.db.reset_to_defaults()
            self.load_blocks()
            messagebox.showinfo("Успех", "Структура отчёта сброшена к умолчаниям!", parent=self.window)
