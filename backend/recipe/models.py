from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import validators
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиентов для рецептов."""
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=settings.RECIPE_CHAR_FIELD_LENG,
        )
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=settings.RECIPE_CHAR_FIELD_LENG, )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                name='Unique_measure_for_ingredient',
                fields=('name', 'measurement_unit'), ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class IngredientAmount(models.Model):
    """Модель количество ингридиентов в блюде."""
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(validators.MinValueValidator(
            1, 'Не может быть меньше 1.'),),)
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты, связанные с рецептом', )
    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепты, содержащие ингредиенты', )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('ingredient__name',)
        constraints = [
            models.UniqueConstraint(
                name='Unique_ingredient_in_recipe',
                fields=['recipe', 'ingredient']),
        ]

    def __str__(self):
        return (f'{self.ingredient.name}'
                f'{self.amount}'
                f'{self.ingredient.measurement_unit}')


class Tag(models.Model):
    """Модель тэгов рецептов."""
    color = models.CharField(
        verbose_name='Код цвета',
        max_length=7,
        default='#ffffff',)

    name = models.CharField(
        verbose_name='Тег',
        max_length=settings.RECIPE_CHAR_FIELD_LENG,
        unique=True, )
    slug = models.SlugField(
        verbose_name='Slug для тега',
        max_length=200,
        unique=True, )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель таблицы списка рецептов."""
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.RECIPE_CHAR_FIELD_LENG)
    text = models.TextField(verbose_name='Описание рецепта', )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            validators.MinValueValidator(
                1, 'Значение не может быть менее 1 минуты.'),))
    tags = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through=IngredientAmount,
        verbose_name='Список ингредиентов',)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'
            )
        ]

    def __str__(self):
        return f'Рецепт "{self.name}" от {self.author}'


class Favorites(models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        related_name='favorite',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user', 'recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное.'


class Carts(models.Model):
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('user', 'recipe')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в cписок покупок.'
