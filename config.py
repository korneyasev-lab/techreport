# config.py
# Файл для хранения настроек логики и структуры отчётов.

import os

# --- Папки ---
REPORTS_FOLDER = "reports"
TEMPLATES_FOLDER = "templates"

# --- Настройки отчётов ---
TOTAL_BLOCKS = 3  # Количество блоков в отчёте (объединили: 2+3 и 4+5)
COMMENT_HEIGHT = 3  # Высота поля для комментария в строках

# --- Структура блоков отчёта ---
REPORT_BLOCKS = {
    "block_1": {
        "title": "Входной контроль сырья",
        "elements": [
            {
                "type": "checkbox_group",
                "label": "Были ли отклонения в сырье? (отметьте все что применимо)",
                "items": [
                    "Отклонения по цвету",
                    "Растекаемость ниже нормы",
                    "Вода выше нормы",
                    "Время набора прочности выше нормы",
                    "Другие отклонения"
                ]
            },
            {
                "type": "text_large",
                "label": "Номера партий и комментарий:",
                "height": 4,
                "placeholder": "Партии: ...\nКомментарий: ..."
            }
        ]
    },

    "block_2": {
        "title": "Контроль технологических параметров и оборудования",
        "elements": [
            {
                "type": "checkbox_group",
                "label": "Технологические параметры (отметьте участки, где всё в порядке):",
                "items": [
                    "Формовка блоков",
                    "Формовка пробок",
                    "Формовка стаканов",
                    "Термообработка",
                    "Сварка",
                    "Упаковка"
                ]
            },
            {
                "type": "text_medium",
                "label": "Комментарий по технологии:",
                "height": 2
            },
            {
                "type": "checkbox_group",
                "label": "Оборудование (отметьте исправное):",
                "items": [
                    "Смесители",
                    "Весы",
                    "Вибростолы",
                    "Сушила",
                    "Сварочное оборудование",
                    "СИ (приборы)"
                ]
            },
            {
                "type": "text_medium",
                "label": "Комментарий по оборудованию:",
                "height": 2
            }
        ]
    },

    "block_3": {
        "title": "Брак, температура и технологические приёмы",
        "elements": [
            {
                "type": "text_large",
                "label": "Комментарий по браку (если был):",
                "height": 3,
                "placeholder": "Опишите несоответствующую продукцию, причины и принятые меры..."
            },
            {
                "type": "text_small",
                "label": "Температура в цехе (мин/макс за неделю):",
                "placeholder": "18-24°C"
            },
            {
                "type": "text_small",
                "label": "Температура на складе:",
                "placeholder": "15-20°C"
            },
            {
                "type": "yes_no",
                "label": "Использовался ли подогрев изделий?"
            },
            {
                "type": "checkbox_group_with_text",
                "label": "Другие технологические приёмы:",
                "items": [
                    "Подогрев воды",
                    "Лимонная кислота",
                    "Изменение времени схватывания"
                ],
                "text_field_label": "Другое:"
            },
            {
                "type": "text_large",
                "label": "Общие замечания/рекомендации:",
                "height": 3,
                "placeholder": "Любые дополнительные наблюдения..."
            }
        ]
    }
}


# --- Типы элементов формы ---
ELEMENT_TYPES = {
    "checkbox_group": "Группа чекбоксов",
    "checkbox_group_with_text": "Группа чекбоксов + текстовое поле",
    "text_large": "Большое текстовое поле",
    "text_medium": "Среднее текстовое поле",
    "text_small": "Маленькое текстовое поле (Entry)",
    "yes_no": "Выбор Да/Нет"
}


# --- Функция загрузки структуры отчёта ---
def get_report_blocks():
    """
    Возвращает структуру блоков отчёта.
    Если существует БД - загружает из неё, иначе - из REPORT_BLOCKS.
    """
    database_file = os.path.join("database", "config.db")

    if os.path.exists(database_file):
        # Загружаем из БД
        try:
            from database import ConfigDatabase
            db = ConfigDatabase()
            structure = db.get_report_structure()

            # Обновляем TOTAL_BLOCKS
            global TOTAL_BLOCKS
            TOTAL_BLOCKS = len(structure)

            return structure
        except Exception as e:
            print(f"Ошибка загрузки из БД: {e}")
            # Возвращаем дефолтную структуру
            return REPORT_BLOCKS
    else:
        # БД нет, возвращаем дефолтную структуру
        return REPORT_BLOCKS