# editor.py
# Графический редактор структуры отчётов

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import configgui
from database import ConfigDatabase
import config
from question_editor_full import QuestionEditorDialog


class QuestionEditorWindow:
    """Окно редактора вопросов отчёта."""

    def __init__(self, parent):
        self.parent = parent
        self.db = ConfigDatabase()

        # Создаём отдельное окно
        self.window = tk.Toplevel(parent)
        self.window.title("Редактор структуры отчёта")
        self.window.geometry("1400x800")
        self.window.configure(bg=configgui.COLORS["bg"])

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
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["title_bg"]
        ).pack(fill=tk.X, pady=10, ipady=10)

        # Основной контейнер с тремя панелями
        main_frame = tk.Frame(self.window, bg=configgui.COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ========== ЛЕВАЯ ПАНЕЛЬ: РАЗДЕЛЫ ==========
        left_frame = tk.LabelFrame(main_frame, text="📋 РАЗДЕЛЫ", font=self.FONT_MEDIUM, padx=10, pady=10, bg=configgui.COLORS["bg"], fg=configgui.COLORS["label_fg"])
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
        blocks_btn_frame = tk.Frame(left_frame, bg=configgui.COLORS["bg"])
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
        center_frame = tk.LabelFrame(main_frame, text="❓ ВОПРОСЫ РАЗДЕЛА", font=self.FONT_MEDIUM, padx=10, pady=10, bg=configgui.COLORS["bg"], fg=configgui.COLORS["label_fg"])
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
        questions_btn_frame = tk.Frame(center_frame, bg=configgui.COLORS["bg"])
        questions_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            questions_btn_frame,
            text="✏️ Редактировать вопрос",
            font=self.FONT_MEDIUM,
            command=self.edit_question,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            height=2
        ).pack(fill=tk.X, pady=5)

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

        move_frame = tk.Frame(questions_btn_frame, bg=configgui.COLORS["bg"])
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

        # Настройка grid весов (только две колонки)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # ========== НИЖНЯЯ ПАНЕЛЬ: КНОПКИ ==========
        bottom_frame = tk.Frame(self.window, bg=configgui.COLORS["bg"])
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

        # Очистка вопросов
        self.questions_listbox.delete(0, tk.END)

    def load_questions(self, block_id):
        """Загружает список вопросов для выбранного раздела."""
        self.questions_listbox.delete(0, tk.END)
        self.questions = self.db.get_questions_by_block(block_id)

        for i, question in enumerate(self.questions):
            display_text = f"{i+1}. {question['label'][:50]}..."
            self.questions_listbox.insert(tk.END, display_text)

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

    def edit_question(self):
        """Открывает полноценный редактор вопроса в отдельном окне."""
        if not self.selected_question_id:
            messagebox.showwarning("Ошибка", "Выберите вопрос для редактирования!", parent=self.window)
            return

        # Открываем диалог редактора
        dialog = QuestionEditorDialog(self.window, self.selected_question_id, self.db)
        result = dialog.show()

        # Если успешно сохранено - обновляем список
        if result:
            self.load_questions(self.selected_block_id)

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
