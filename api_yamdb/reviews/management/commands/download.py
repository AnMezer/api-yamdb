import csv
import os
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand, CommandParser
from django.db import connection, transaction
from django.db.models.base import ModelBase

from users.models import User

from .exceptions import CantDeleteDataError, ModelNotFoundError

# Запуск из корня проекта:
# python .\api_yamdb\manage.py download api_yamdb\static\data
# --reviews обязательный параметр - название приложения. По умолчанию reviews.
# --clean необязательный параметр. если установлен,
# --createsuperuser необязательный параметр. если установлен,
# будет создан суперюзер с параметрами из константы SUPERUSER.
# --splitter необязательный параметр. если установлен,
# указывает разделитель в CSV файлах. По умолчанию запятая.
# перед сохранением таблицы будут очищены
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

SUPERUSER = {
    'username': 'admin',
    'email': 'admin@admin.ru',
    'password': 'admin',
    'role': 3
}


class Command(BaseCommand):
    help = 'Импорт данных из CSV файла в базу данных приложения'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('path', type=str,
                            help='Путь к папке с CSV файлами')
        parser.add_argument('--app', type=str, default='reviews',
                            help='Приложение для импорта')
        parser.add_argument('--splitter', type=str, default=',',
                            help='Разделитель (по уполчанию: , (запятая))')
        parser.add_argument('--clean', action='store_true',
                            help='Очистить таблицы перед записью')
        parser.add_argument('--createsuperuser', action='store_true',
                            help='Добавить аккаунт суперюзера')

    def check_files(self, path: str) -> None:
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
            error_message = (f'Файл(ы) не найден(ы): '
                             f'{", ".join(not_exist_files)}')
            raise FileNotFoundError(error_message)

    def get_model(self, app: str, table: str) -> ModelBase:
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
            raise ModelNotFoundError(error_message)

    def clean_row(
            self, row: dict, table: str) -> dict[str, str | int | None] | None:
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
                    dt_datetime = datetime.fromisoformat(dt_iso)  # noqa
                    cleaned_row[field] = value
                except Exception:
                    return None

            # Если данные изначально корректны, сохраняем, как есть
            else:
                cleaned_row[field] = value

        return cleaned_row

    def delete_table(self, table: str, app: str) -> None:
        """Очищает таблицу в приложении, сохраняя структуру

        Args:
            table: Название таблицы
            app: Название приложения

        Raises:
            CantDeleteData: В случае ошибки при удалении.
        """
        if table == 'user':
            table_name = 'users_user'
        else:
            table_name = f'{app}_{table}'
        querys = [
            # Очищает данные в таблице
            f'DELETE FROM {table_name}',

            # Обнуляет счетчик id, ранее использованные можно применять снова
            f"DELETE FROM sqlite_sequence WHERE name='{table_name}'"
        ]
        try:
            for query in querys:
                with connection.cursor() as cursor:
                    cursor.execute(query)
            self.stdout.write(self.style.NOTICE(
                f'Таблица {table_name} очищена'))
        except Exception as e:
            raise CantDeleteDataError(
                f'Ошибка при очистке таблицы {table}: {e}')

    def delete_data(self, clean: bool, app: str) -> None:
        """Последовательно отправляет запрос на очистку таблиц в БД

        Args:
            clean: Флаг, нужна ли очистка
            app: Приложение, в котором очищаются таблицы
        """
        if clean:
            # Таблицу с логами django тоже чистим, в ней ссылки на User
            # Без ее очистки не очистить таблицу с пользователями
            self.delete_table('admin_log', 'django')

            tables = IMPORT_QUEUE + M2M_TABLES
            for table in reversed(tables):
                self.delete_table(table, app)

    def add_superuser(self, createsuperuser: bool) -> None:
        """Добавляет учетку супервользователя

        Args:
            createsuperuser: флаг - необходимо ли создание записи
        """
        if createsuperuser:
            User.objects.create_superuser(**SUPERUSER)
            self.stdout.write(self.style.SUCCESS('superuser создан'))

    def handle(self, *args, **options):
        """Создает записи В БД, импортируя их из CSV файлов.
        Перед сохранением выполняет валидацию значений полей,
        Записи с невалидными полями не сохраняются.

        При наличии флагов:
            --clean - предварительно очищает БД
            --createsuperuser - создает в БД усетку суперюзера
        """
        self.check_files(options['path'])
        self.delete_data(options['clean'], options['app'])

        for table in IMPORT_QUEUE:

            try:
                file_path = os.path.join(options['path'], f'{table}.csv')
                if table == 'user':
                    model = self.get_model('users', table)
                else:
                    model = self.get_model(options['app'], table)

                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=options['splitter'])
                    rows = list(reader)
                    with transaction.atomic():
                        for row in rows:
                            cleaned_row = self.clean_row(row, table)
                            if cleaned_row:
                                model.objects.create(**cleaned_row)
                self.stdout.write(self.style.SUCCESS(
                    f'Таблица {table} загружена'))
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
                query = (f'INSERT INTO {table_name} ({columns}) '
                         f'VALUES ({empty_values})')

                with connection.cursor() as cursor:
                    for row in rows:
                        cleaned_row = self.clean_row(row, table)
                        if cleaned_row:
                            values = ([cleaned_row[key]
                                       for key in rows[0].keys()])
                            cursor.execute(query, values)
                self.stdout.write(self.style.SUCCESS(
                    f'Таблица {table} загружена'))
        self.add_superuser(options['createsuperuser'])
