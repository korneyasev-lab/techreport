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

    def validate_block_data(self, block_num):
        """
        Валидация данных блока (пока не используется, но можно добавить).
        Возвращает (success, error_message).
        """
        # TODO: Добавить валидацию обязательных полей
        return True, None

    def save_report(self):
        """
        Сохраняет отчёт в текстовый файл.
        Возвращает (success, result), где result - имя файла или текст ошибки.
        """
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
        for block_num in range(1, config.TOTAL_BLOCKS + 1):
            block_key = f"block_{block_num}"
            block_data = config.REPORT_BLOCKS[block_key]

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
        (Заглушка для будущего функционала архива)
        """
        if not os.path.exists(config.REPORTS_FOLDER):
            return []

        reports = []
        for filename in os.listdir(config.REPORTS_FOLDER):
            if filename.endswith('.txt'):
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