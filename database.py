# database.py
# Модуль для работы с базой данных SQLite (структура отчётов)

import sqlite3
import os
import config


DATABASE_FOLDER = "database"
DATABASE_FILE = os.path.join(DATABASE_FOLDER, "config.db")


class ConfigDatabase:
    """Класс для работы с базой данных конфигурации отчётов."""

    def __init__(self):
        self._ensure_database_folder()
        self.conn = None
        self.cursor = None

    def _ensure_database_folder(self):
        """Создаёт папку для БД, если её нет."""
        if not os.path.exists(DATABASE_FOLDER):
            os.makedirs(DATABASE_FOLDER)

    def connect(self):
        """Подключается к базе данных."""
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.conn.row_factory = sqlite3.Row  # Доступ по именам колонок
        self.cursor = self.conn.cursor()

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def init_database(self):
        """
        Инициализирует базу данных: создаёт таблицы и заполняет данными из config.py.
        Вызывается при первом запуске или при сбросе к умолчаниям.
        """
        self.connect()

        # Создание таблиц
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_key TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                sort_order INTEGER NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_id INTEGER NOT NULL,
                question_type TEXT NOT NULL,
                label TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                height INTEGER DEFAULT NULL,
                placeholder TEXT DEFAULT NULL,
                text_field_label TEXT DEFAULT NULL,
                FOREIGN KEY (block_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS question_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        ''')

        # Проверяем, есть ли уже данные
        self.cursor.execute('SELECT COUNT(*) FROM blocks')
        count = self.cursor.fetchone()[0]

        if count == 0:
            # Заполняем данными из config.py
            self._populate_from_config()

        self.conn.commit()
        self.close()

    def _populate_from_config(self):
        """Заполняет БД данными из config.py."""
        for block_num in range(1, config.TOTAL_BLOCKS + 1):
            block_key = f"block_{block_num}"
            block_data = config.REPORT_BLOCKS[block_key]

            # Вставка блока
            self.cursor.execute(
                'INSERT INTO blocks (block_key, title, sort_order) VALUES (?, ?, ?)',
                (block_key, block_data['title'], block_num)
            )
            block_id = self.cursor.lastrowid

            # Вставка вопросов
            for i, element in enumerate(block_data['elements']):
                question_type = element['type']
                label = element['label']
                height = element.get('height', None)
                placeholder = element.get('placeholder', None)
                text_field_label = element.get('text_field_label', None)

                self.cursor.execute('''
                    INSERT INTO questions
                    (block_id, question_type, label, sort_order, height, placeholder, text_field_label)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (block_id, question_type, label, i + 1, height, placeholder, text_field_label))

                question_id = self.cursor.lastrowid

                # Вставка вариантов ответов (если есть)
                if 'items' in element:
                    for j, item in enumerate(element['items']):
                        self.cursor.execute('''
                            INSERT INTO question_options (question_id, option_text, sort_order)
                            VALUES (?, ?, ?)
                        ''', (question_id, item, j + 1))

    # ============================================================
    # МЕТОДЫ ЧТЕНИЯ ДАННЫХ
    # ============================================================

    def get_all_blocks(self):
        """Возвращает все блоки (разделы) отчёта в порядке sort_order."""
        self.connect()
        self.cursor.execute('SELECT * FROM blocks ORDER BY sort_order')
        blocks = self.cursor.fetchall()
        self.close()
        return blocks

    def get_questions_by_block(self, block_id):
        """Возвращает все вопросы для указанного блока."""
        self.connect()
        self.cursor.execute(
            'SELECT * FROM questions WHERE block_id = ? ORDER BY sort_order',
            (block_id,)
        )
        questions = self.cursor.fetchall()
        self.close()
        return questions

    def get_question_options(self, question_id):
        """Возвращает все варианты ответов для вопроса."""
        self.connect()
        self.cursor.execute(
            'SELECT * FROM question_options WHERE question_id = ? ORDER BY sort_order',
            (question_id,)
        )
        options = self.cursor.fetchall()
        self.close()
        return options

    def get_report_structure(self):
        """
        Возвращает полную структуру отчёта в формате, совместимом с config.REPORT_BLOCKS.
        Используется для генерации GUI форм.
        """
        structure = {}
        blocks = self.get_all_blocks()

        for block in blocks:
            block_key = block['block_key']
            questions = self.get_questions_by_block(block['id'])

            elements = []
            for question in questions:
                element = {
                    'type': question['question_type'],
                    'label': question['label']
                }

                # Добавляем дополнительные поля
                if question['height']:
                    element['height'] = question['height']
                if question['placeholder']:
                    element['placeholder'] = question['placeholder']
                if question['text_field_label']:
                    element['text_field_label'] = question['text_field_label']

                # Получаем варианты ответов
                if question['question_type'] in ['checkbox_group', 'checkbox_group_with_text']:
                    options = self.get_question_options(question['id'])
                    element['items'] = [opt['option_text'] for opt in options]

                elements.append(element)

            structure[block_key] = {
                'title': block['title'],
                'elements': elements
            }

        return structure

    # ============================================================
    # МЕТОДЫ ИЗМЕНЕНИЯ ДАННЫХ
    # ============================================================

    def add_block(self, title):
        """Добавляет новый блок в конец списка."""
        self.connect()
        self.cursor.execute('SELECT MAX(sort_order) FROM blocks')
        max_order = self.cursor.fetchone()[0] or 0

        # Генерируем новый block_key
        self.cursor.execute('SELECT COUNT(*) FROM blocks')
        count = self.cursor.fetchone()[0]
        new_key = f"block_{count + 1}"

        self.cursor.execute(
            'INSERT INTO blocks (block_key, title, sort_order) VALUES (?, ?, ?)',
            (new_key, title, max_order + 1)
        )
        self.conn.commit()
        block_id = self.cursor.lastrowid
        self.close()
        return block_id

    def update_block_title(self, block_id, new_title):
        """Обновляет название блока."""
        self.connect()
        self.cursor.execute('UPDATE blocks SET title = ? WHERE id = ?', (new_title, block_id))
        self.conn.commit()
        self.close()

    def delete_block(self, block_id):
        """Удаляет блок и все его вопросы (CASCADE)."""
        self.connect()
        self.cursor.execute('DELETE FROM blocks WHERE id = ?', (block_id,))
        self.conn.commit()
        self.close()

    def add_question(self, block_id, question_type, label, height=None, placeholder=None):
        """Добавляет новый вопрос в блок."""
        self.connect()
        self.cursor.execute(
            'SELECT MAX(sort_order) FROM questions WHERE block_id = ?',
            (block_id,)
        )
        max_order = self.cursor.fetchone()[0] or 0

        self.cursor.execute('''
            INSERT INTO questions
            (block_id, question_type, label, sort_order, height, placeholder)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (block_id, question_type, label, max_order + 1, height, placeholder))

        self.conn.commit()
        question_id = self.cursor.lastrowid
        self.close()
        return question_id

    def update_question(self, question_id, label, question_type, height=None, placeholder=None, text_field_label=None):
        """Обновляет параметры вопроса."""
        self.connect()
        self.cursor.execute('''
            UPDATE questions
            SET label = ?, question_type = ?, height = ?, placeholder = ?, text_field_label = ?
            WHERE id = ?
        ''', (label, question_type, height, placeholder, text_field_label, question_id))
        self.conn.commit()
        self.close()

    def delete_question(self, question_id):
        """Удаляет вопрос и все его варианты (CASCADE)."""
        self.connect()
        self.cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        self.conn.commit()
        self.close()

    def add_option(self, question_id, option_text):
        """Добавляет новый вариант ответа к вопросу."""
        self.connect()
        self.cursor.execute(
            'SELECT MAX(sort_order) FROM question_options WHERE question_id = ?',
            (question_id,)
        )
        max_order = self.cursor.fetchone()[0] or 0

        self.cursor.execute('''
            INSERT INTO question_options (question_id, option_text, sort_order)
            VALUES (?, ?, ?)
        ''', (question_id, option_text, max_order + 1))

        self.conn.commit()
        option_id = self.cursor.lastrowid
        self.close()
        return option_id

    def update_option(self, option_id, new_text):
        """Обновляет текст варианта ответа."""
        self.connect()
        self.cursor.execute(
            'UPDATE question_options SET option_text = ? WHERE id = ?',
            (new_text, option_id)
        )
        self.conn.commit()
        self.close()

    def delete_option(self, option_id):
        """Удаляет вариант ответа."""
        self.connect()
        self.cursor.execute('DELETE FROM question_options WHERE id = ?', (option_id,))
        self.conn.commit()
        self.close()

    def move_question_up(self, question_id):
        """Перемещает вопрос вверх в списке."""
        self.connect()
        # Получаем текущий вопрос
        self.cursor.execute('SELECT block_id, sort_order FROM questions WHERE id = ?', (question_id,))
        row = self.cursor.fetchone()
        if not row:
            self.close()
            return

        block_id, current_order = row['block_id'], row['sort_order']

        if current_order <= 1:
            self.close()
            return  # Уже первый

        # Находим предыдущий вопрос
        self.cursor.execute('''
            SELECT id FROM questions
            WHERE block_id = ? AND sort_order = ?
        ''', (block_id, current_order - 1))

        prev_row = self.cursor.fetchone()
        if prev_row:
            prev_id = prev_row['id']
            # Меняем местами
            self.cursor.execute('UPDATE questions SET sort_order = ? WHERE id = ?', (current_order, prev_id))
            self.cursor.execute('UPDATE questions SET sort_order = ? WHERE id = ?', (current_order - 1, question_id))
            self.conn.commit()

        self.close()

    def move_question_down(self, question_id):
        """Перемещает вопрос вниз в списке."""
        self.connect()
        self.cursor.execute('SELECT block_id, sort_order FROM questions WHERE id = ?', (question_id,))
        row = self.cursor.fetchone()
        if not row:
            self.close()
            return

        block_id, current_order = row['block_id'], row['sort_order']

        # Находим следующий вопрос
        self.cursor.execute('''
            SELECT id FROM questions
            WHERE block_id = ? AND sort_order = ?
        ''', (block_id, current_order + 1))

        next_row = self.cursor.fetchone()
        if next_row:
            next_id = next_row['id']
            # Меняем местами
            self.cursor.execute('UPDATE questions SET sort_order = ? WHERE id = ?', (current_order, next_id))
            self.cursor.execute('UPDATE questions SET sort_order = ? WHERE id = ?', (current_order + 1, question_id))
            self.conn.commit()

        self.close()

    def reset_to_defaults(self):
        """Сбрасывает БД к настройкам по умолчанию из config.py."""
        self.connect()

        # Удаляем все данные
        self.cursor.execute('DELETE FROM question_options')
        self.cursor.execute('DELETE FROM questions')
        self.cursor.execute('DELETE FROM blocks')

        # Заполняем заново
        self._populate_from_config()

        self.conn.commit()
        self.close()


def ensure_database_initialized():
    """
    Проверяет наличие БД и инициализирует её при необходимости.
    Вызывается при запуске приложения.
    """
    if not os.path.exists(DATABASE_FILE):
        db = ConfigDatabase()
        db.init_database()
