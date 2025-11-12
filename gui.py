# gui.py
# Графический интерфейс приложения. Только отрисовка и события.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import calendar
import configgui
import config
from logic import ReportLogic
from database import ConfigDatabase
from editor import QuestionEditorWindow


class ReportApp:
    """Главный класс приложения с GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title(configgui.APP_TITLE)

        # --- Адаптация настроек под ОС ---
        fonts, padding = configgui.get_settings()
        self.fonts = fonts
        self.padding = padding

        self.FONT_TITLE = ("Arial", self.fonts["title"], "bold")
        self.FONT_LARGE = ("Arial", self.fonts["large"], "bold")
        self.FONT_MEDIUM = ("Arial", self.fonts["medium"])
        self.FONT_SMALL = ("Arial", self.fonts["small"])
        self.FONT_MAIN_BUTTON = ("Arial", self.fonts["main_button"])
        self.FONT_README = ("Arial", 14)  # README шрифт 14

        # Настройка стилей ttk
        style = ttk.Style()
        style.configure("TButton",
                       background=configgui.COLORS["button_bg"],
                       foreground=configgui.COLORS["button_fg"])
        style.configure("TEntry",
                       fieldbackground=configgui.COLORS["text_bg"],
                       foreground=configgui.COLORS["text_fg"])
        style.configure("TCombobox",
                       fieldbackground=configgui.COLORS["text_bg"],
                       foreground=configgui.COLORS["text_fg"])

        # Разворачиваем окно на весь экран
        try:
            self.root.state('zoomed')
        except tk.TclError:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")

        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Логика
        self.logic = ReportLogic()

        # GUI данные
        self.current_block = 1
        self.current_widgets = {}

        # Загрузка структуры отчёта из БД или config.py
        self.report_blocks = config.get_report_blocks()

        self.show_main_screen()

    def clear_container(self):
        """Очищает главный контейнер перед показом нового экрана."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    # ============================================================
    # ГЛАВНЫЙ ЭКРАН
    # ============================================================

    def show_main_screen(self):
        """Показывает главный экран с README слева и кнопками справа."""
        self.clear_container()

        # Заголовок
        tk.Label(
            self.main_container,
            text=configgui.MAIN_SCREEN_TITLE,
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=15)

        # Контейнер для двух колонок
        content_frame = tk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40)

        # ЛЕВАЯ КОЛОНКА - README
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        readme_frame = tk.LabelFrame(
            left_frame,
            text="📖 Инструкция",
            font=("Arial", self.fonts["medium"], "bold"),
            padx=20,
            pady=15
        )
        readme_frame.pack(fill=tk.BOTH, expand=True)

        readme_label = tk.Label(
            readme_frame,
            text=configgui.README_TEXT.strip(),
            font=self.FONT_README,
            justify=tk.LEFT,
            anchor='nw',
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"]
        )
        readme_label.pack(fill=tk.BOTH, expand=True)

        # ПРАВАЯ КОЛОНКА - Кнопки
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Отступ сверху чтобы кнопки были по центру
        tk.Frame(right_frame, height=100).pack()

        tk.Button(
            right_frame,
            text=configgui.START_BTN,
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.show_report_params_screen
        ).pack(pady=self.padding["pady"] * 3)

        tk.Button(
            right_frame,
            text=configgui.ARCHIVE_BTN,
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.show_archive
        ).pack(pady=self.padding["pady"] * 3)

        tk.Button(
            right_frame,
            text="⚙️ Редактор вопросов",
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.open_editor
        ).pack(pady=self.padding["pady"] * 3)

        tk.Button(
            right_frame,
            text=configgui.EXIT_BTN,
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.root.quit
        ).pack(pady=self.padding["pady"] * 3)

    # ============================================================
    # ЭКРАН ВЫБОРА ПАРАМЕТРОВ ОТЧЁТА
    # ============================================================

    def show_report_params_screen(self):
        """Показывает экран выбора параметров отчёта."""
        self.clear_container()

        tk.Label(
            self.main_container,
            text="Параметры отчёта",
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=15)

        form_frame = tk.Frame(self.main_container)
        form_frame.pack(expand=True, pady=20)

        # Год
        tk.Label(form_frame, text="Год:", font=self.FONT_MEDIUM, fg=configgui.COLORS["label_fg"]).grid(
            row=0, column=0, sticky="w", pady=5, padx=5
        )
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_entry = tk.Entry(
            form_frame, textvariable=self.year_var, font=self.FONT_MEDIUM, width=32,
            bg=configgui.COLORS["text_bg"], fg=configgui.COLORS["text_fg"]
        )
        year_entry.grid(row=0, column=1, padx=self.padding["padx"], pady=5)
        self._update_weeks_timer = None
        self.year_var.trace_add("write", self._schedule_update_weeks)

        # Месяц
        tk.Label(form_frame, text="Месяц:", font=self.FONT_MEDIUM, fg=configgui.COLORS["label_fg"]).grid(
            row=1, column=0, sticky="w", pady=5, padx=5
        )
        self.month_var = tk.StringVar()
        month_combo = ttk.Combobox(
            form_frame, textvariable=self.month_var, values=configgui.MONTHS,
            font=self.FONT_MEDIUM, state="readonly", width=30
        )
        month_combo.grid(row=1, column=1, padx=self.padding["padx"], pady=5)
        month_combo.set(configgui.MONTHS[datetime.now().month - 1])
        month_combo.bind("<<ComboboxSelected>>", self._schedule_update_weeks)

        # Неделя
        tk.Label(form_frame, text="Неделя:", font=self.FONT_MEDIUM, fg=configgui.COLORS["label_fg"]).grid(
            row=2, column=0, sticky="w", pady=5, padx=5
        )
        self.week_var = tk.StringVar()
        self.week_combo = ttk.Combobox(
            form_frame, textvariable=self.week_var,
            font=self.FONT_MEDIUM, state="disabled", width=30
        )
        self.week_combo.grid(row=2, column=1, padx=self.padding["padx"], pady=5)

        # Отложенное заполнение недель для быстрой загрузки окна
        self.root.after(1, self._update_weeks)

        # Кнопки
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(
            btn_frame, text="Начать заполнение",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.start_report
        ).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(
            btn_frame, text="Назад",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.show_main_screen
        ).pack(side=tk.LEFT, padx=10, pady=5)

    def _schedule_update_weeks(self, *args):
        """Планирует обновление недель с задержкой для избежания множественных вызовов."""
        if self._update_weeks_timer:
            self.root.after_cancel(self._update_weeks_timer)
        self._update_weeks_timer = self.root.after(300, self._update_weeks)

    def _get_week_ranges_for_month(self, year, month_index):
        """Генерирует список недель с датами для указанного месяца."""
        weeks = []
        month = month_index + 1
        cal = calendar.monthcalendar(year, month)

        for week_days in cal:
            month_days = [d for d in week_days if d != 0]
            if not month_days:
                continue

            first_day = month_days[0]
            first_date = date(year, month, first_day)
            monday = first_date - timedelta(days=first_date.weekday())
            friday = monday + timedelta(days=4)

            week_num = monday.isocalendar()[1]
            month_str = configgui.MONTHS_GENITIVE[friday.month - 1]

            week_str = f"Неделя {week_num} ({monday.day} - {friday.day} {month_str})"
            weeks.append(week_str)
        return weeks

    def _update_weeks(self, *args):
        """Обновляет выпадающий список недель при смене года или месяца."""
        try:
            year = int(self.year_var.get())
            month_index = configgui.MONTHS.index(self.month_var.get())
        except (ValueError, IndexError):
            self.week_combo.set("")
            self.week_combo.config(values=[], state="disabled")
            return

        week_options = self._get_week_ranges_for_month(year, month_index)
        self.week_combo.config(values=week_options, state="readonly")

        current_date = datetime.now()
        if year == current_date.year and month_index == current_date.month - 1:
            current_week_num = current_date.isocalendar()[1]
            for option in week_options:
                if f"Неделя {current_week_num}" in option:
                    self.week_combo.set(option)
                    return

        if week_options:
            self.week_combo.set(week_options[0])
        else:
            self.week_combo.set("")

    def start_report(self):
        """Проверяет параметры и запускает экран заполнения отчета."""
        # Валидация года
        try:
            year = int(self.year_var.get())
            if year < 2000 or year > 2100:
                messagebox.showerror(
                    configgui.DIALOG_TITLES["error"],
                    "Год должен быть в диапазоне 2000-2100"
                )
                return
        except ValueError:
            messagebox.showerror(
                configgui.DIALOG_TITLES["error"],
                "Год должен быть числом"
            )
            return

        # Валидация месяца
        month = self.month_var.get()
        if not month or month not in configgui.MONTHS:
            messagebox.showwarning(
                configgui.DIALOG_TITLES["warning"],
                "Пожалуйста, выберите месяц"
            )
            return

        # Валидация недели
        week = self.week_var.get()
        if not week:
            messagebox.showwarning(
                configgui.DIALOG_TITLES["warning"],
                configgui.DIALOG_MESSAGES["no_week_selected"]
            )
            return

        # Инициализация отчёта в логике
        self.logic.init_report(
            week=week,
            year=str(year),
            month=month
        )

        self.current_block = 1
        self.show_block_screen()

    # ============================================================
    # ЭКРАН ЗАПОЛНЕНИЯ БЛОКА
    # ============================================================

    def show_block_screen(self):
        """Показывает экран для заполнения текущего блока."""
        self.clear_container()

        block_key = f"block_{self.current_block}"
        block_data = self.report_blocks[block_key]

        # Кнопка возврата в главное меню
        top_frame = tk.Frame(self.main_container)
        top_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            top_frame,
            text="← В главное меню",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.confirm_exit_to_main,
            width=20
        ).pack(side=tk.LEFT, padx=20)

        # Заголовок
        header = f"Отчёт: {self.logic.report_params['week']}"
        tk.Label(
            self.main_container,
            text=header,
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=5)

        # Прогресс
        progress_text = f"Блок {self.current_block} из {config.TOTAL_BLOCKS}: {block_data['title']}"
        tk.Label(
            self.main_container,
            text=progress_text,
            font=self.FONT_LARGE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=3)

        # Canvas для прокрутки
        canvas_frame = tk.Frame(self.main_container)
        canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, padx=40)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Создание элементов блока
        self.current_widgets = {}
        for i, element in enumerate(block_data['elements']):
            self.create_element(scrollable_frame, block_key, i, element)

        # Кнопки навигации
        self.create_navigation_buttons()

    # ============================================================
    # СОЗДАНИЕ ЭЛЕМЕНТОВ ФОРМЫ
    # ============================================================

    def create_element(self, parent, block_key, element_index, element_data):
        """Создает элемент формы в зависимости от типа."""
        element_key = f"{block_key}_element_{element_index}"
        element_type = element_data['type']

        if element_type == "checkbox_group":
            self.create_checkbox_group(parent, element_key, element_data)

        elif element_type == "text_large":
            self.create_text_field(parent, element_key, element_data, height=element_data.get('height', 4))

        elif element_type == "text_medium":
            self.create_text_field(parent, element_key, element_data, height=element_data.get('height', 2))

        elif element_type == "text_small":
            self.create_entry_field(parent, element_key, element_data)

        elif element_type == "yes_no":
            self.create_yes_no_field(parent, element_key, element_data)

        elif element_type == "checkbox_group_with_text":
            self.create_checkbox_group_with_text(parent, element_key, element_data)

    def create_checkbox_group(self, parent, element_key, element_data):
        """Создает группу чекбоксов."""
        frame = tk.LabelFrame(
            parent,
            text=element_data['label'],
            font=self.FONT_MEDIUM,
            padx=10,
            pady=5
        )
        frame.pack(pady=5, fill=tk.X)

        checkbox_vars = []
        for item in element_data['items']:
            var = tk.BooleanVar(value=False)

            # Восстановление значения из логики
            saved_value = self.logic.get_answer(element_key)
            if saved_value and item in saved_value:
                var.set(True)

            cb = tk.Checkbutton(
                frame,
                text=item,
                variable=var,
                font=self.FONT_LARGE,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            )
            cb.pack(anchor="w", pady=2)
            checkbox_vars.append((item, var))

        self.current_widgets[element_key] = checkbox_vars

    def create_text_field(self, parent, element_key, element_data, height=4):
        """Создает многострочное текстовое поле с белым фоном."""
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(
            frame,
            text=element_data['label'],
            font=self.FONT_MEDIUM
        ).pack(anchor="w", pady=2)

        text_widget = tk.Text(
            frame,
            height=height,
            font=self.FONT_LARGE,
            wrap=tk.WORD,
            bg=configgui.COLORS["text_bg"],  # Белый фон
            fg=configgui.COLORS["text_fg"],  # Чёрный текст
            insertbackground=configgui.COLORS["text_fg"]  # Чёрный курсор
        )
        text_widget.pack(fill=tk.X, pady=2)

        # Восстановление значения из логики
        saved_value = self.logic.get_answer(element_key)
        if saved_value:
            text_widget.insert("1.0", saved_value)
        elif 'placeholder' in element_data:
            # Placeholder
            text_widget.insert("1.0", element_data['placeholder'])
            text_widget.config(fg='grey')

            def on_focus_in(event):
                if text_widget.get("1.0", "end-1c") == element_data['placeholder']:
                    text_widget.delete("1.0", tk.END)
                    text_widget.config(fg=configgui.COLORS["text_fg"])

            def on_focus_out(event):
                if not text_widget.get("1.0", "end-1c").strip():
                    text_widget.insert("1.0", element_data['placeholder'])
                    text_widget.config(fg='grey')

            text_widget.bind("<FocusIn>", on_focus_in)
            text_widget.bind("<FocusOut>", on_focus_out)

        self.current_widgets[element_key] = text_widget

    def create_entry_field(self, parent, element_key, element_data):
        """Создает однострочное поле ввода."""
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(
            frame,
            text=element_data['label'],
            font=self.FONT_MEDIUM
        ).pack(anchor="w", pady=2)

        entry_var = tk.StringVar()

        # Восстановление значения из логики
        saved_value = self.logic.get_answer(element_key)
        if saved_value:
            entry_var.set(saved_value)

        entry = tk.Entry(
            frame,
            textvariable=entry_var,
            font=self.FONT_LARGE,
            width=40,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"]
        )
        entry.pack(anchor="w", pady=2)

        # Placeholder
        if 'placeholder' in element_data and not saved_value:
            entry.insert(0, element_data['placeholder'])
            entry.config(fg='grey')

            def on_focus_in(event):
                if entry.get() == element_data['placeholder']:
                    entry.delete(0, tk.END)
                    entry.config(fg='black')

            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, element_data['placeholder'])
                    entry.config(fg='grey')

            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        self.current_widgets[element_key] = entry_var

    def create_yes_no_field(self, parent, element_key, element_data):
        """Создает поле с выбором Да/Нет."""
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill=tk.X)

        tk.Label(
            frame,
            text=element_data['label'],
            font=self.FONT_MEDIUM
        ).pack(anchor="w", pady=2)

        answer_var = tk.StringVar()

        # Восстановление значения из логики
        saved_value = self.logic.get_answer(element_key)
        if saved_value:
            answer_var.set(saved_value)

        button_frame = tk.Frame(frame)
        button_frame.pack(anchor="w", pady=2)

        def set_answer(value):
            answer_var.set(value)
            update_buttons()

        def update_buttons():
            current = answer_var.get()
            if current == "Да":
                btn_yes.config(bg=configgui.COLORS["yes_active"], fg=configgui.COLORS["text_yes"])
                btn_no.config(bg=configgui.COLORS["no_inactive"], fg="black")
            elif current == "Нет":
                btn_yes.config(bg=configgui.COLORS["yes_inactive"], fg="black")
                btn_no.config(bg=configgui.COLORS["no_active"], fg=configgui.COLORS["text_no"])
            else:
                btn_yes.config(bg=configgui.COLORS["yes_inactive"], fg="black")
                btn_no.config(bg=configgui.COLORS["no_inactive"], fg="black")

        btn_yes = tk.Button(
            button_frame,
            text="ДА",
            font=self.FONT_LARGE,
            width=8,
            command=lambda: set_answer("Да")
        )
        btn_yes.pack(side=tk.LEFT, padx=5)

        btn_no = tk.Button(
            button_frame,
            text="НЕТ",
            font=self.FONT_LARGE,
            width=8,
            command=lambda: set_answer("Нет")
        )
        btn_no.pack(side=tk.LEFT, padx=5)

        update_buttons()
        self.current_widgets[element_key] = answer_var

    def create_checkbox_group_with_text(self, parent, element_key, element_data):
        """Создает группу чекбоксов с дополнительным текстовым полем."""
        frame = tk.LabelFrame(
            parent,
            text=element_data['label'],
            font=self.FONT_MEDIUM,
            padx=10,
            pady=5
        )
        frame.pack(pady=5, fill=tk.X)

        checkbox_vars = []
        for item in element_data['items']:
            var = tk.BooleanVar(value=False)

            # Восстановление значения из логики
            saved_value = self.logic.get_answer(element_key)
            if saved_value and isinstance(saved_value, dict):
                if item in saved_value.get('checkboxes', []):
                    var.set(True)

            cb = tk.Checkbutton(
                frame,
                text=item,
                variable=var,
                font=self.FONT_LARGE,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"]
            )
            cb.pack(anchor="w", pady=2)
            checkbox_vars.append((item, var))

        # Текстовое поле "Другое"
        other_frame = tk.Frame(frame)
        other_frame.pack(fill=tk.X, pady=2)

        tk.Label(
            other_frame,
            text=element_data.get('text_field_label', 'Другое:'),
            font=self.FONT_MEDIUM
        ).pack(anchor="w")

        text_var = tk.StringVar()

        # Восстановление текста из логики
        saved_value = self.logic.get_answer(element_key)
        if saved_value and isinstance(saved_value, dict):
            if 'text' in saved_value:
                text_var.set(saved_value['text'])

        entry = tk.Entry(
            other_frame,
            textvariable=text_var,
            font=self.FONT_LARGE,
            width=50,
            bg=configgui.COLORS["text_bg"],
            fg=configgui.COLORS["text_fg"]
        )
        entry.pack(fill=tk.X, pady=2)

        self.current_widgets[element_key] = {
            'checkboxes': checkbox_vars,
            'text': text_var
        }

    # ============================================================
    # НАВИГАЦИЯ
    # ============================================================

    def create_navigation_buttons(self):
        """Создает кнопки навигации внизу экрана."""
        btn_frame = tk.Frame(self.main_container)
        btn_frame.pack(pady=10, fill=tk.X)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # Кнопка "Назад"
        if self.current_block > 1:
            btn_back = tk.Button(
                btn_frame,
                text="← Назад",
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=self.prev_block,
                width=20
            )
            btn_back.grid(row=0, column=0, sticky="e", padx=20, pady=5)

        # Кнопка "Далее" или "Сохранить"
        if self.current_block < config.TOTAL_BLOCKS:
            btn_next = tk.Button(
                btn_frame,
                text="Далее →",
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=self.next_block,
                width=20
            )
            btn_next.grid(row=0, column=1, sticky="w", padx=20, pady=5)
        else:
            btn_save = tk.Button(
                btn_frame,
                text="Сохранить отчёт",
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=self.save_report,
                width=20
            )
            btn_save.grid(row=0, column=1, sticky="w", padx=20, pady=5)

    def save_current_block_data(self):
        """Сохраняет данные текущего блока в логику."""
        for element_key, widget in self.current_widgets.items():
            if isinstance(widget, list):  # checkbox_group
                selected = [item for item, var in widget if var.get()]
                self.logic.save_answer(element_key, selected)

            elif isinstance(widget, dict):  # checkbox_group_with_text
                selected = [item for item, var in widget['checkboxes'] if var.get()]
                text = widget['text'].get().strip()
                self.logic.save_answer(element_key, {
                    'checkboxes': selected,
                    'text': text
                })

            elif isinstance(widget, tk.Text):  # text_large/medium
                text = widget.get("1.0", "end-1c").strip()
                # Не сохранять placeholder
                block_key = f"block_{self.current_block}"
                block_data = self.report_blocks[block_key]
                element_index = int(element_key.split('_')[-1])
                placeholder = block_data['elements'][element_index].get('placeholder', '')
                if text and text != placeholder:
                    self.logic.save_answer(element_key, text)

            else:  # StringVar (entry или yes_no)
                value = widget.get().strip()
                # Не сохранять placeholder
                block_key = f"block_{self.current_block}"
                block_data = self.report_blocks[block_key]
                element_index = int(element_key.split('_')[-1])
                placeholder = block_data['elements'][element_index].get('placeholder', '')
                if value and value != placeholder:
                    self.logic.save_answer(element_key, value)

    def prev_block(self):
        """Переход к предыдущему блоку."""
        self.save_current_block_data()
        self.current_block -= 1
        self.show_block_screen()

    def next_block(self):
        """Переход к следующему блоку."""
        self.save_current_block_data()
        self.current_block += 1
        self.show_block_screen()

    def confirm_exit_to_main(self):
        """Подтверждение выхода в главное меню."""
        confirm = messagebox.askyesno(
            "Выход в главное меню",
            "Вы уверены, что хотите вернуться в главное меню?\n\nНесохранённые данные будут потеряны."
        )
        if confirm:
            self.show_main_screen()

    def save_report(self):
        """Сохраняет отчёт через логику с валидацией."""
        self.save_current_block_data()

        # Валидация отчёта
        valid, error_message = self.logic.validate_report()
        if not valid:
            messagebox.showwarning(
                configgui.DIALOG_TITLES["warning"],
                error_message
            )
            return

        # Показываем диалог выбора формата
        self.show_export_format_dialog()

    def show_export_format_dialog(self):
        """Показывает диалог выбора формата экспорта."""
        # Создаём модальное окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор формата экспорта")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()

        # Центрируем окно
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Контент
        tk.Label(
            dialog,
            text="Выберите формат для сохранения отчёта:",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=20)

        # Переменная для выбранного формата
        format_var = tk.StringVar(value="pdf")

        # Радиокнопки
        formats_frame = tk.Frame(dialog)
        formats_frame.pack(pady=10)

        tk.Radiobutton(
            formats_frame,
            text="PDF (Portable Document Format)",
            variable=format_var,
            value="pdf",
            font=self.FONT_LARGE,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"]
        ).pack(anchor="w", pady=5)

        tk.Radiobutton(
            formats_frame,
            text="DOCX (Microsoft Word)",
            variable=format_var,
            value="docx",
            font=self.FONT_LARGE,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"]
        ).pack(anchor="w", pady=5)

        tk.Radiobutton(
            formats_frame,
            text="TXT (Текстовый файл)",
            variable=format_var,
            value="txt",
            font=self.FONT_LARGE,
            fg=configgui.COLORS["label_fg"],
            bg=configgui.COLORS["bg"]
        ).pack(anchor="w", pady=5)

        # Кнопки
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=20)

        def on_save():
            export_format = format_var.get()
            dialog.destroy()
            self.execute_save_report(export_format)

        def on_cancel():
            dialog.destroy()

        tk.Button(
            buttons_frame,
            text="Сохранить",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=on_save,
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(
            buttons_frame,
            text="Отмена",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=on_cancel,
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Ждём закрытия диалога
        dialog.wait_window()

    def execute_save_report(self, export_format):
        """Выполняет сохранение отчёта в выбранном формате."""
        success, result = self.logic.save_report(export_format=export_format)

        if success:
            messagebox.showinfo(
                configgui.DIALOG_TITLES["success"],
                configgui.DIALOG_MESSAGES["report_saved"].format(
                    filename=result,
                    folder=config.REPORTS_FOLDER
                )
            )
            self.show_main_screen()
        else:
            messagebox.showerror(
                configgui.DIALOG_TITLES["error"],
                configgui.DIALOG_MESSAGES["save_error"].format(error=result)
            )

    # ============================================================
    # АРХИВ
    # ============================================================

    def show_archive(self):
        """Показывает экран архива с возможностью просмотра и удаления отчётов."""
        self.clear_container()

        # Заголовок
        tk.Label(
            self.main_container,
            text=configgui.ARCHIVE_TITLE,
            font=self.FONT_TITLE,
            fg=configgui.COLORS["label_fg"]
        ).pack(pady=15)

        # Получаем список отчётов
        reports = self.logic.get_all_reports()

        if not reports:
            # Если отчётов нет
            empty_frame = tk.Frame(self.main_container)
            empty_frame.pack(expand=True)

            tk.Label(
                empty_frame,
                text="Архив пуст\n\nСоздайте первый отчёт!",
                font=self.FONT_LARGE,
                fg=configgui.COLORS["label_fg"],
                justify=tk.CENTER
            ).pack(pady=40)

            tk.Button(
                empty_frame,
                text="< Назад",
                font=self.FONT_MEDIUM,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=self.show_main_screen
            ).pack(pady=5)
            return

        # Фрейм для списка отчётов с прокруткой
        list_frame = tk.Frame(self.main_container)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # Canvas для прокрутки
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Заголовки таблицы
        header_frame = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=1)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            header_frame,
            text="Имя файла",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            width=40,
            anchor="w"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tk.Label(
            header_frame,
            text="Дата создания",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            width=20,
            anchor="w"
        ).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(
            header_frame,
            text="Действия",
            font=self.FONT_MEDIUM,
            fg=configgui.COLORS["label_fg"],
            width=20
        ).grid(row=0, column=2, padx=10, pady=5)

        # Строки с отчётами
        for i, report in enumerate(reports):
            row_frame = tk.Frame(
                scrollable_frame,
                relief=tk.GROOVE,
                borderwidth=1,
                bg="white" if i % 2 == 0 else "#f5f5f5"
            )
            row_frame.pack(fill=tk.X, pady=2)

            # Имя файла
            tk.Label(
                row_frame,
                text=report['filename'],
                font=self.FONT_SMALL,
                fg=configgui.COLORS["label_fg"],
                width=40,
                anchor="w",
                bg=row_frame["bg"]
            ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

            # Дата создания
            tk.Label(
                row_frame,
                text=report['created'],
                font=self.FONT_SMALL,
                fg=configgui.COLORS["label_fg"],
                width=20,
                bg=row_frame["bg"]
            ).grid(row=0, column=1, padx=10, pady=8)

            # Кнопки действий
            actions_frame = tk.Frame(row_frame, bg=row_frame["bg"])
            actions_frame.grid(row=0, column=2, padx=10, pady=5)

            tk.Button(
                actions_frame,
                text="Просмотр",
                font=self.FONT_SMALL,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=lambda f=report['filename']: self.open_report(f),
                width=10
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                actions_frame,
                text="Удалить",
                font=self.FONT_SMALL,
                bg=configgui.COLORS["button_bg"],
                fg=configgui.COLORS["button_fg"],
                command=lambda f=report['filename']: self.delete_report(f),
                width=10
            ).pack(side=tk.LEFT, padx=5)

        # Кнопка назад внизу
        bottom_frame = tk.Frame(self.main_container)
        bottom_frame.pack(pady=15)

        tk.Button(
            bottom_frame,
            text="< Назад",
            font=self.FONT_MEDIUM,
            bg=configgui.COLORS["button_bg"],
            fg=configgui.COLORS["button_fg"],
            command=self.show_main_screen
        ).pack(pady=5)

    def open_report(self, filename):
        """Открывает отчёт в системном просмотрщике."""
        import os
        import subprocess
        import platform

        filepath = os.path.join(config.REPORTS_FOLDER, filename)

        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # Linux
                subprocess.call(('xdg-open', filepath))
        except Exception as e:
            messagebox.showerror(
                configgui.DIALOG_TITLES["error"],
                f"Не удалось открыть файл:\n{e}"
            )

    def delete_report(self, filename):
        """Удаляет отчёт после подтверждения."""
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить отчёт:\n\n{filename}\n\nЭто действие необратимо!"
        )

        if confirm:
            success, message = self.logic.delete_report(filename)

            if success:
                messagebox.showinfo(
                    configgui.DIALOG_TITLES["success"],
                    message
                )
                # Обновляем экран архива
                self.show_archive()
            else:
                messagebox.showerror(
                    configgui.DIALOG_TITLES["error"],
                    message
                )

    # ============================================================
    # РЕДАКТОР ВОПРОСОВ
    # ============================================================

    def open_editor(self):
        """Открывает окно редактора вопросов."""
        QuestionEditorWindow(self.root)