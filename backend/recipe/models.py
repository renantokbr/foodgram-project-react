from django.conf import settings
from django.core import validators
from django.db import models

from users.models import User


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
    ingredients = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиенты, связанные с рецептом', )
    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Рецепты, содержащие ингредиенты', )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                name='Unique_ingredient_in_recipe',
                fields=('ingredients', 'recipe')),
        )

    def __str__(self):
        return f'{self.recipe}: {self.amount}, {self.ingredients}'


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
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through=IngredientAmount,
        verbose_name='Список ингредиентов',
        related_name='recipes')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/')
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.RECIPE_CHAR_FIELD_LENG)

    tags = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги')
    text = models.TextField(verbose_name='Описание рецепта', )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (models.UniqueConstraint(
            name='unique_per_author',
            fields=('name', 'author')),)

    def __str__(self):
        return self.name


class RecipeBase(models.Model):
    """Модель базы рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Favorites(RecipeBase):
    """Модель избранных рецептов."""
    class Meta(RecipeBase.Meta):
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite_recipe'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class Carts(RecipeBase):
    """Модель корзины."""
    class Meta(RecipeBase.Meta):
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
