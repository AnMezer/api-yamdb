import csv
import os
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, transaction
from django.apps import apps
from datetime import datetime

from reviews.models import Category, Genre, Title
from .exceptions import ModelNotFound, CantDeleteData

# Запуск из корня проекта:
# python .\api_yamdb\manage.py download api_yamdb/static/data --reviews --clean
# --reviews обязательный параметр - название приложения
# --clean необязательный параметр. если установлен, перед сохранением таблицы будут очищены 
# Слэши можно использовать любые, модуль os сам все исправит, как нужно.

# Имена файлов должны соответствовать именам моделей
# Порядок загрузки такой, чтобы при загрузке данных в модель,
# модель с которой она имеет связанные поля была уже загружена.
IMPORT_QUEUE = [
    'user',
    'category',
    'genre',
    'title',
    'review',
    'comment'
]

# Таблицы в БД связывающие ManyToManyFields
M2M_TABLES = ['title_genre']


class Command(BaseCommand):
    help = 'Импорт данных из CSV файла в базу данных приложения'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('path', type=str, help='Путь к папке с CSV файлами')
        parser.add_argument('--app', type=str, default='reviews',
                            help='Приложение для импорта')
        parser.add_argument('--splitter', type=str, default=',',
                            help='Разделитель (по уполчанию: , (запятая))')
        parser.add_argument('--clean', action='store_true',
                            help='Очистить таблицы перед записью')

    def check_files(self, path):
        """Проверяет наличие файлов в папке

        Args:
            path: Путь к папке с файлами
        Raises:
            FileNotFoundError: Если файл отсутствует
        """
        not_exist_files = []
        tables = IMPORT_QUEUE + M2M_TABLES
        for table in tables:
            file_path = os.path.join(path, f'{table}.csv')
            if not os.path.exists(f'{file_path}'):
                not_exist_files.append(f'{table}.csv')
        if not_exist_files:
            error_message = f'Файл(ы) не найден(ы): {", ".join(not_exist_files)}'
            raise FileNotFoundError(error_message)

    def get_model(self, app, table):
        """Возвращает модель приложения по названию таблицы

        Args:
            app: Название приложения
            table: Название таблицы

        Raises:
            ModelNotFound: Если модель не найдена
        """
        try:
            model = apps.get_model(app, table)
            return model
        except (LookupError, ValueError) as e:
            error_message = (
                f'Ошибка при поиске модели {table} в приложении {app}. {e}')
            raise ModelNotFound(error_message)

    def clean_row(self, row: dict, table: str):
        """Проверяет на корректность значения полей

        Args:
            row: Словарь с исходными полями

        Returns:
            cleaned_row - если значения пригодны для записи в БД
            None - если значения использовать нельзя.
        """
        cleaned_row: dict[str, str | int | None] = {}
        for field, value in row.items():

            # Проверяем, что значения полей ForeignKey можно привести к int
            if field.endswith('_id'):
                try:
                    cleaned_row[field] = int(value)
                except Exception:
                    return None

            # Проверяем корректность даты
            elif field == 'pub_date':
                try:
                    # Пробуем преобразовать value -> iso -> datetime
                    dt_iso = value.replace('Z', '+00:00')
                    dt_datetime = datetime.fromisoformat(dt_iso)
                    cleaned_row[field] = value
                except Exception:
                    return None

            # Если данные изначально корректны, сохраняем, как есть
            else:
                cleaned_row[field] = value

        return cleaned_row

    def delete_table(self, table, app):
        table_name = f'{app}_{table}'
        querys = [
            f'DELETE FROM {table_name}',
            f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"
        ]
        try:
            for query in querys:
                with connection.cursor() as cursor:
                    cursor.execute(query)
        except Exception as e:
            raise CantDeleteData(f'Ошибка при очистке таблицы {table}: {e}')

    def delete_data(self, clean, app):
        if clean:
            self.delete_table('admin_log', 'django')
            tables = IMPORT_QUEUE + M2M_TABLES
            for table in reversed(tables):
                self.delete_table(table, app)

    def handle(self, *args, **options):
        self.check_files(options['path'])
        self.delete_data(options['clean'], options['app'])

        for table in IMPORT_QUEUE:

            try:
                file_path = os.path.join(options['path'], f'{table}.csv')

                model = self.get_model(options['app'], table)

                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=options['splitter'])
                    rows = list(reader)
                    with transaction.atomic():
                        for row in rows:
                            cleaned_row = self.clean_row(row, table)
                            if cleaned_row:
                                model.objects.create(**cleaned_row)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'{e}'))

        for table in M2M_TABLES:
            file_path = os.path.join(options['path'], f'{table}.csv')

            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=options['splitter'])
                rows = list(reader)

                # Получаем строку с именами столбцов
                columns = ', '.join(rows[0].keys())

                # Заполнители для SQL запроса = числу столбцов
                empty_values = ', '.join(['%s'] * len(rows[0].keys()))

                table_name = f'{options["app"]}_{table}'

                # Формируем SQL запрос
                query = f'INSERT INTO {table_name} ({columns}) VALUES ({empty_values})'

                with connection.cursor() as cursor:
                    for row in rows:
                        cleaned_row = self.clean_row(row, table)
                        if cleaned_row:
                            values = [cleaned_row[key] for key in rows[0].keys()]
                            cursor.execute(query, values)
