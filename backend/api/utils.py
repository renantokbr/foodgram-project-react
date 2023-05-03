import csv
from datetime import datetime as dt
from django.http.response import HttpResponse
from recipe.models import IngredientAmount


def prepare_file(user, ingredients, filename='list_of_ingredients.txt'):
    create_time = dt.now().strftime('%d.%m.%Y %H:%M')

    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    writer = csv.writer(response)
    writer.writerow([f'Список покупок пользователя: {user.first_name}', ])
    writer.writerow([f'{create_time}', ])
    writer.writerow(['', ])
    writer.writerow(['Ингредиент', 'Количество', 'Единицы измерения'])
    for ingredient in ingredients:
        writer.writerow(
            [
                ingredient['ingredient'],
                ingredient['sum_amount'],
                ingredient['measure']
            ]
        )

    return response


def set_of_ingredients(recipe, ingredients):
    for ingredient in ingredients:
        IngredientAmount.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount']
        )
