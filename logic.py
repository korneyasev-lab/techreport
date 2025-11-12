# logic.py
# Бизнес-логика приложения: сохранение отчётов, валидация данных.

import os
from datetime import datetime
import config


class ReportLogic:
    """Класс для работы с логикой отчётов."""

    def __init__(self):
        self.report_params = {}
        self.answers = {}
        self._ensure_folders()
        # Загрузка структуры отчёта из БД или config.py
        self.report_blocks = config.get_report_blocks()

    def _ensure_folders(self):
        """Создаёт необходимые папки, если их нет."""
        for folder in [config.REPORTS_FOLDER, config.TEMPLATES_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def init_report(self, week, year, month):
        """Инициализирует новый отчёт."""
        self.report_params = {
            "week": week,
            "year": year,
            "month": month,
            "created_at": datetime.now().strftime('%d.%m.%Y %H:%M')
        }
        self.answers = {}

    def save_answer(self, element_key, value):
        """Сохраняет ответ на элемент формы."""
        self.answers[element_key] = value

    def get_answer(self, element_key):
        """Получает сохранённый ответ."""
        return self.answers.get(element_key, None)

    def validate_report(self):
        """
        Валидация всего отчёта перед сохранением.
        Возвращает (success, error_message).
        """
        # Проверяем, что хотя бы одно поле заполнено
        if not self.answers:
            return False, "Отчёт полностью пустой. Заполните хотя бы одно поле."

        # Проверка блока 1 - должны быть указаны либо отклонения, либо комментарий
        block1_has_data = False
        for key in self.answers:
            if key.startswith('block_1_'):
                value = self.answers[key]
                if value:  # Не пустое значение
                    if isinstance(value, list) and len(value) > 0:
                        block1_has_data = True
                        break
                    elif isinstance(value, str) and value.strip():
                        block1_has_data = True
                        break

        # Проверка блока 2 - должны быть отмечены участки или оборудование
        block2_has_data = False
        for key in self.answers:
            if key.startswith('block_2_'):
                value = self.answers[key]
                if value:
                    if isinstance(value, list) and len(value) > 0:
                        block2_has_data = True
                        break
                    elif isinstance(value, str) and value.strip():
                        block2_has_data = True
                        break

        # Проверка блока 3 - должна быть заполнена хотя бы температура
        block3_has_data = False
        for key in self.answers:
            if key.startswith('block_3_'):
                value = self.answers[key]
                if value:
                    if isinstance(value, str) and value.strip():
                        block3_has_data = True
                        break
                    elif isinstance(value, dict):
                        if value.get('checkboxes') or value.get('text'):
                            block3_has_data = True
                            break

        # Хотя бы один блок должен быть заполнен
        if not (block1_has_data or block2_has_data or block3_has_data):
            return False, "Необходимо заполнить хотя бы один блок отчёта."

        return True, None

    def save_report(self, export_format='txt'):
        """
        Сохраняет отчёт в указанном формате.
        export_format: 'txt', 'pdf', 'docx'
        Возвращает (success, result), где result - имя файла или текст ошибки.
        """
        if export_format == 'pdf':
            return self._save_report_pdf()
        elif export_format == 'docx':
            return self._save_report_docx()
        else:
            return self._save_report_txt()

    def _save_report_txt(self):
        """Сохраняет отчёт в текстовый файл."""
        try:
            # Формирование имени файла
            week_str = self.report_params['week'].replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
            filename = f"Отчёт_{week_str}_{self.report_params['year']}.txt"
            filepath = os.path.join(config.REPORTS_FOLDER, filename)

            # Запись отчёта
            with open(filepath, "w", encoding="utf-8") as f:
                self._write_report_header(f)
                self._write_report_blocks(f)
                self._write_report_footer(f)

            return True, filename

        except Exception as e:
            return False, str(e)

    def _write_report_header(self, file):
        """Записывает заголовок отчёта."""
        file.write("=" * 70 + "\n")
        file.write("ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ КОНТРОЛЯ ТЕХНОЛОГИИ\n")
        file.write("=" * 70 + "\n\n")
        file.write(f"Период: {self.report_params['week']}\n")
        file.write(f"Год: {self.report_params['year']}\n")
        file.write(f"Месяц: {self.report_params['month']}\n")
        file.write(f"Дата создания: {self.report_params['created_at']}\n")
        file.write("\n" + "=" * 70 + "\n\n")

    def _write_report_blocks(self, file):
        """Записывает данные всех блоков."""
        for block_num in range(1, len(self.report_blocks) + 1):
            block_key = f"block_{block_num}"
            block_data = self.report_blocks[block_key]

            file.write(f"\n{block_data['title'].upper()}\n")
            file.write("-" * 70 + "\n\n")

            for i, element in enumerate(block_data['elements']):
                element_key = f"{block_key}_element_{i}"

                if element_key in self.answers:
                    answer = self.answers[element_key]

                    file.write(f"{element['label']}\n")

                    if isinstance(answer, list):
                        # Список чекбоксов
                        if answer:
                            for item in answer:
                                file.write(f"  ✓ {item}\n")
                        else:
                            file.write("  (нет отмеченных пунктов)\n")

                    elif isinstance(answer, dict):
                        # Чекбоксы + текст
                        if answer.get('checkboxes'):
                            for item in answer['checkboxes']:
                                file.write(f"  ✓ {item}\n")
                        if answer.get('text'):
                            file.write(f"  Другое: {answer['text']}\n")

                    else:
                        # Текст или Да/Нет
                        file.write(f"  {answer}\n")

                    file.write("\n")

    def _write_report_footer(self, file):
        """Записывает подвал отчёта."""
        file.write("\n" + "=" * 70 + "\n")
        file.write("КОНЕЦ ОТЧЁТА\n")
        file.write("=" * 70 + "\n")

    def get_all_reports(self):
        """
        Возвращает список всех сохранённых отчётов.
        Поддерживает форматы: .txt, .pdf, .docx
        """
        if not os.path.exists(config.REPORTS_FOLDER):
            return []

        reports = []
        allowed_extensions = ('.txt', '.pdf', '.docx')

        for filename in os.listdir(config.REPORTS_FOLDER):
            if filename.endswith(allowed_extensions):
                filepath = os.path.join(config.REPORTS_FOLDER, filename)
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%d.%m.%Y %H:%M'),
                    'size': stat.st_size
                })

        # Сортировка по дате создания (новые сверху)
        reports.sort(key=lambda x: x['created'], reverse=True)
        return reports

    def delete_report(self, filename):
        """
        Удаляет отчёт по имени файла.
        Возвращает (success, message).
        """
        try:
            filepath = os.path.join(config.REPORTS_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, f"Отчёт '{filename}' успешно удалён."
            else:
                return False, "Файл не найден."
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"

    # ============================================================
    # ЭКСПОРТ В PDF
    # ============================================================

    def _save_report_pdf(self):
        """Сохраняет отчёт в PDF формат."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            return False, "Библиотека reportlab не установлена. Установите: pip install reportlab"

        try:
            # Формирование имени файла
            week_str = self.report_params['week'].replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
            filename = f"Отчёт_{week_str}_{self.report_params['year']}.pdf"
            filepath = os.path.join(config.REPORTS_FOLDER, filename)

            # Создание PDF документа
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            # Попытка зарегистрировать шрифт с поддержкой кириллицы
            try:
                # Пытаемся найти системный шрифт
                import platform
                if platform.system() == 'Windows':
                    font_path = 'C:/Windows/Fonts/arial.ttf'
                elif platform.system() == 'Darwin':  # macOS
                    font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
                else:  # Linux
                    font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'

                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                    font_name = 'CustomFont'
                else:
                    font_name = 'Helvetica'
            except:
                font_name = 'Helvetica'

            # Стили
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=6,
                leading=14
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=font_name,
                fontSize=14,
                spaceAfter=3,
                spaceBefore=3,
                leading=14
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=14,
                spaceAfter=2,
                leading=14
            )

            # Контент
            story = []

            # Заголовок
            story.append(Paragraph("ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ КОНТРОЛЯ ТЕХНОЛОГИИ", title_style))
            story.append(Spacer(1, 0.2*cm))

            # Параметры отчёта
            story.append(Paragraph(f"Период: {self.report_params['week']}", normal_style))
            story.append(Paragraph(f"Год: {self.report_params['year']}", normal_style))
            story.append(Paragraph(f"Месяц: {self.report_params['month']}", normal_style))
            story.append(Paragraph(f"Дата создания: {self.report_params['created_at']}", normal_style))
            story.append(Spacer(1, 0.4*cm))

            # Блоки
            for block_num in range(1, len(self.report_blocks) + 1):
                block_key = f"block_{block_num}"
                block_data = self.report_blocks[block_key]

                story.append(Paragraph(block_data['title'].upper(), heading_style))
                story.append(Spacer(1, 0.15*cm))

                for i, element in enumerate(block_data['elements']):
                    element_key = f"{block_key}_element_{i}"

                    if element_key in self.answers:
                        answer = self.answers[element_key]

                        # Убираем HTML-теги из label
                        label = element['label'].replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(f"<b>{label}</b>", normal_style))

                        if isinstance(answer, list):
                            if answer:
                                for item in answer:
                                    item_text = item.replace('<', '&lt;').replace('>', '&gt;')
                                    story.append(Paragraph(f"☑ {item_text}", normal_style))
                            else:
                                story.append(Paragraph("(нет отмеченных пунктов)", normal_style))

                        elif isinstance(answer, dict):
                            if answer.get('checkboxes'):
                                for item in answer['checkboxes']:
                                    item_text = item.replace('<', '&lt;').replace('>', '&gt;')
                                    story.append(Paragraph(f"☑ {item_text}", normal_style))
                            if answer.get('text'):
                                text = answer['text'].replace('<', '&lt;').replace('>', '&gt;')
                                story.append(Paragraph(f"Другое: {text}", normal_style))

                        else:
                            answer_text = str(answer).replace('<', '&lt;').replace('>', '&gt;')
                            story.append(Paragraph(answer_text, normal_style))

                        story.append(Spacer(1, 0.1*cm))

                story.append(Spacer(1, 0.25*cm))

            # Генерация PDF
            doc.build(story)

            return True, filename

        except Exception as e:
            return False, f"Ошибка при создании PDF: {str(e)}"

    # ============================================================
    # ЭКСПОРТ В DOCX
    # ============================================================

    def _save_report_docx(self):
        """Сохраняет отчёт в DOCX формат."""
        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            return False, "Библиотека python-docx не установлена. Установите: pip install python-docx"

        try:
            # Формирование имени файла
            week_str = self.report_params['week'].replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
            filename = f"Отчёт_{week_str}_{self.report_params['year']}.docx"
            filepath = os.path.join(config.REPORTS_FOLDER, filename)

            # Создание документа
            doc = Document()

            # Заголовок
            title = doc.add_heading('ЕЖЕНЕДЕЛЬНЫЙ ОТЧЁТ КОНТРОЛЯ ТЕХНОЛОГИИ', level=0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in title.runs:
                run.font.size = Pt(16)
            title_format = title.paragraph_format
            title_format.line_spacing = 1.0
            title_format.space_after = Pt(6)

            # Параметры отчёта
            for text in [
                f"Период: {self.report_params['week']}",
                f"Год: {self.report_params['year']}",
                f"Месяц: {self.report_params['month']}",
                f"Дата создания: {self.report_params['created_at']}"
            ]:
                p = doc.add_paragraph(text)
                for run in p.runs:
                    run.font.size = Pt(14)
                p_format = p.paragraph_format
                p_format.line_spacing = 1.0
                p_format.space_after = Pt(3)

            # Пустая строка
            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(6)

            # Блоки
            for block_num in range(1, len(self.report_blocks) + 1):
                block_key = f"block_{block_num}"
                block_data = self.report_blocks[block_key]

                # Заголовок блока
                heading = doc.add_heading(block_data['title'].upper(), level=1)
                for run in heading.runs:
                    run.font.size = Pt(16)
                heading_format = heading.paragraph_format
                heading_format.line_spacing = 1.0
                heading_format.space_before = Pt(6)
                heading_format.space_after = Pt(3)

                for i, element in enumerate(block_data['elements']):
                    element_key = f"{block_key}_element_{i}"

                    if element_key in self.answers:
                        answer = self.answers[element_key]

                        # Label
                        p = doc.add_paragraph()
                        run = p.add_run(element['label'])
                        run.bold = True
                        run.font.size = Pt(14)
                        p_format = p.paragraph_format
                        p_format.line_spacing = 1.0
                        p_format.space_after = Pt(2)

                        if isinstance(answer, list):
                            if answer:
                                for item in answer:
                                    item_p = doc.add_paragraph(f"✓ {item}", style='List Bullet')
                                    for run in item_p.runs:
                                        run.font.size = Pt(14)
                                    item_p_format = item_p.paragraph_format
                                    item_p_format.line_spacing = 1.0
                                    item_p_format.space_after = Pt(2)
                            else:
                                empty_p = doc.add_paragraph("(нет отмеченных пунктов)")
                                for run in empty_p.runs:
                                    run.font.size = Pt(14)
                                empty_p.paragraph_format.line_spacing = 1.0
                                empty_p.paragraph_format.space_after = Pt(2)

                        elif isinstance(answer, dict):
                            if answer.get('checkboxes'):
                                for item in answer['checkboxes']:
                                    item_p = doc.add_paragraph(f"✓ {item}", style='List Bullet')
                                    for run in item_p.runs:
                                        run.font.size = Pt(14)
                                    item_p_format = item_p.paragraph_format
                                    item_p_format.line_spacing = 1.0
                                    item_p_format.space_after = Pt(2)
                            if answer.get('text'):
                                text_p = doc.add_paragraph(f"Другое: {answer['text']}")
                                for run in text_p.runs:
                                    run.font.size = Pt(14)
                                text_p.paragraph_format.line_spacing = 1.0
                                text_p.paragraph_format.space_after = Pt(2)

                        else:
                            ans_p = doc.add_paragraph(str(answer))
                            for run in ans_p.runs:
                                run.font.size = Pt(14)
                            ans_p.paragraph_format.line_spacing = 1.0
                            ans_p.paragraph_format.space_after = Pt(2)

                        # Минимальный отступ после элемента
                        element_spacer = doc.add_paragraph()
                        element_spacer.paragraph_format.space_after = Pt(3)

            # Сохранение документа
            doc.save(filepath)

            return True, filename

        except Exception as e:
            return False, f"Ошибка при создании DOCX: {str(e)}"