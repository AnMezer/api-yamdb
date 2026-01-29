import csv
import os
from pprint import pprint
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.apps import apps

from reviews.models import Category, Genre, Title

# Запуск из корня проекта:
# python .\api_yamdb\manage.py download api_yamdb/static/data


class Command(BaseCommand):
    help = 'Импорт данных из CSV файла в базу данных'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('path', type=str, help='Путь к папке с CSV файлами')
        parser.add_argument('--app', type=str, default='reviews',
                            help='Приложение для импорта')
        parser.add_argument('--splitter', type=str, default=',',
                            help='Разделитель (по уполчанию: , (запятая))')

    def handle(self, *args, **options):

        # Получаем список файлов для импорта
        csv_files_path = os.path.join(os.getcwd(), options['path'])
        files_for_import = os.listdir(csv_files_path)

        # Получаем словарь {ожидаемое имя файла: модель}
        app_models = apps.get_app_config(options['app']).get_models()
        models_dict = {model.__name__.lower(): model for model in app_models}

        for file in files_for_import:
            if not file.endswith('.csv'):
                continue
            file_name, _ = os.path.splitext(file)
            file_path = os.path.join(csv_files_path, file)

            model = models_dict.get(file_name)

            if not model:
                print(f'Для файла {file} модель не найдена')
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=options['splitter'])
                rows = list(reader)
                with transaction.atomic():
                    for row in rows:
                        model.objects.create(**row)
