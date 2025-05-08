import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from data/ingredients.csv'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'

        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # пропустить заголовки

            Ingredient.objects.all().delete()
            count = 0
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Загружено {count} ингредиентов'))
