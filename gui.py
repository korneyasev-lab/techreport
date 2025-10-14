# gui.py
# Графический интерфейс приложения. Только отрисовка и события.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import calendar
import configgui
import config
from logic import ReportLogic


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
        ttk.Label(
            self.main_container,
            text=configgui.MAIN_SCREEN_TITLE,
            font=self.FONT_TITLE
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
            font=self.FONT_README,  # README шрифт 14
            justify=tk.LEFT,
            anchor='nw'
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
            command=self.show_report_params_screen
        ).pack(pady=self.padding["pady"] * 3)

        tk.Button(
            right_frame,
            text=configgui.ARCHIVE_BTN,
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            command=self.show_archive
        ).pack(pady=self.padding["pady"] * 3)

        tk.Button(
            right_frame,
            text=configgui.EXIT_BTN,
            font=self.FONT_MAIN_BUTTON,
            width=25,
            height=2,
            command=self.root.quit
        ).pack(pady=self.padding["pady"] * 3)

    # ============================================================
    # ЭКРАН ВЫБОРА ПАРАМЕТРОВ ОТЧЁТА
    # ============================================================

    def show_report_params_screen(self):
        """Показывает экран выбора параметров отчёта."""
        self.clear_container()

        ttk.Label(
            self.main_container,
            text="Параметры отчёта",
            font=self.FONT_TITLE
        ).pack(pady=15)

        form_frame = ttk.Frame(self.main_container, padding=20)
        form_frame.pack(expand=True)

        # Год
        ttk.Label(form_frame, text="Год:", font=self.FONT_MEDIUM).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_entry = ttk.Entry(
            form_frame, textvariable=self.year_var, font=self.FONT_MEDIUM, width=32
        )
        year_entry.grid(row=0, column=1, padx=self.padding["padx"], pady=5)
        self.year_var.trace_add("write", self._update_weeks)

        # Месяц
        ttk.Label(form_frame, text="Месяц:", font=self.FONT_MEDIUM).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.month_var = tk.StringVar()
        month_combo = ttk.Combobox(
            form_frame, textvariable=self.month_var, values=configgui.MONTHS,
            font=self.FONT_MEDIUM, state="readonly", width=30
        )
        month_combo.grid(row=1, column=1, padx=self.padding["padx"], pady=5)
        month_combo.set(configgui.MONTHS[datetime.now().month - 1])
        month_combo.bind("<<ComboboxSelected>>", self._update_weeks)

        # Неделя
        ttk.Label(form_frame, text="Неделя:", font=self.FONT_MEDIUM).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.week_var = tk.StringVar()
        self.week_combo = ttk.Combobox(
            form_frame, textvariable=self.week_var,
            font=self.FONT_MEDIUM, state="disabled", width=30
        )
        self.week_combo.grid(row=2, column=1, padx=self.padding["padx"], pady=5)

        self._update_weeks()  # Первоначальное заполнение недель

        # Кнопки
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        ttk.Button(
            btn_frame, text="Начать заполнение",
            command=self.start_report, padding=10
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame, text="Назад",
            command=self.show_main_screen, padding=10
        ).pack(side=tk.LEFT, padx=10)

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
            year=self.year_var.get(),
            month=self.month_var.get()
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
        block_data = config.REPORT_BLOCKS[block_key]

        # Заголовок
        header = f"Отчёт: {self.logic.report_params['week']}"
        ttk.Label(
            self.main_container,
            text=header,
            font=self.FONT_MEDIUM
        ).pack(pady=5)

        # Прогресс
        progress_text = f"Блок {self.current_block} из {config.TOTAL_BLOCKS}: {block_data['title']}"
        ttk.Label(
            self.main_container,
            text=progress_text,
            font=self.FONT_LARGE
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
                font=self.FONT_LARGE
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
            width=40
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
                font=self.FONT_LARGE
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
            width=50
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
            btn_back = ttk.Button(
                btn_frame,
                text="← Назад",
                command=self.prev_block,
                width=20
            )
            btn_back.grid(row=0, column=0, sticky="e", padx=20)

        # Кнопка "Далее" или "Сохранить"
        if self.current_block < config.TOTAL_BLOCKS:
            btn_next = ttk.Button(
                btn_frame,
                text="Далее →",
                command=self.next_block,
                width=20
            )
            btn_next.grid(row=0, column=1, sticky="w", padx=20)
        else:
            btn_save = ttk.Button(
                btn_frame,
                text="Сохранить отчёт",
                command=self.save_report,
                width=20
            )
            btn_save.grid(row=0, column=1, sticky="w", padx=20)

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
                block_data = config.REPORT_BLOCKS[block_key]
                element_index = int(element_key.split('_')[-1])
                placeholder = block_data['elements'][element_index].get('placeholder', '')
                if text and text != placeholder:
                    self.logic.save_answer(element_key, text)

            else:  # StringVar (entry или yes_no)
                value = widget.get().strip()
                # Не сохранять placeholder
                block_key = f"block_{self.current_block}"
                block_data = config.REPORT_BLOCKS[block_key]
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

    def save_report(self):
        """Сохраняет отчёт через логику."""
        self.save_current_block_data()

        success, result = self.logic.save_report()

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
    # АРХИВ (ЗАГЛУШКА)
    # ============================================================

    def show_archive(self):
        """Показывает экран архива (заглушка)."""
        self.clear_container()

        archive_frame = ttk.Frame(self.main_container, padding=40)
        archive_frame.pack(expand=True)

        ttk.Label(
            archive_frame,
            text=configgui.ARCHIVE_TITLE,
            font=self.FONT_TITLE
        ).pack(pady=(0, 20))

        ttk.Label(
            archive_frame,
            text=configgui.ARCHIVE_PLACEHOLDER_TEXT,
            font=self.FONT_MEDIUM,
            justify=tk.CENTER
        ).pack(pady=40)

        ttk.Button(
            archive_frame,
            text="< Назад",
            command=self.show_main_screen
        ).pack(pady=20)