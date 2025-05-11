import json
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipes.models import Ingredient
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Загружает ингредиенты из JSON файла в базу данных"

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, "data", "ingredients.json")
        self.stdout.write(
            self.style.SUCCESS(f"Ищем файл по пути: {file_path}")
        )

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден."))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ingredients_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Файл {file_path} не найден."))
            return
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR(
                    f"Ошибка декодирования JSON в файле {file_path}."
                )
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Произошла ошибка при чтении файла: {e}")
            )
            return

        count_added = 0
        count_skipped = 0

        for item in ingredients_data:
            try:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=item["name"].lower(),
                    measurement_unit=item[
                        "measurement_unit"
                    ].lower(),  # Приводим к нижнему регистру
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Добавлен ингредиент: {ingredient.name}"
                        )
                    )
                    count_added += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Ингредиент уже существует "
                            f"(пропущен): "
                            f"{ingredient.name}"
                        )
                    )
                    count_skipped += 1
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Ошибка целостности для {item["name"]}: {e}'
                    )
                )
                count_skipped += 1
            except KeyError:
                self.stdout.write(
                    self.style.ERROR(
                        f"Пропущена запись из-за отсутствия ключа "
                        f'"name" или "measurement_unit": {item}'
                    )
                )
                count_skipped += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Не удалось добавить ингредиент "
                        f'{item.get("name", "(имя отсутствует)")}'
                        f": {e}"
                    )
                )
                count_skipped += 1

        success_message = (
            f"Загрузка ингредиентов завершена. Добавлено: {count_added}, "
            f"Пропущено (уже существовали или ошибка): {count_skipped}"
        )
        self.stdout.write(self.style.SUCCESS(success_message))
