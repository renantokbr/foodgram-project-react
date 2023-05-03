from recipe.models import Ingredient, Recipe

from django_filters.rest_framework import (FilterSet,
                                           CharFilter,
                                           BooleanFilter,
                                           AllValuesMultipleFilter,
                                           NumberFilter)


class RecipeFilter(FilterSet):
    """Фильтрация по автору, тэгу, избранному и добавленному в покупки."""
    author = NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
    )

    is_favorited = BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(shopping_cart__user=self.request.user)


class IngredientFilter(FilterSet):
    """Фильтрация ингредиентов"""
    name = CharFilter(label='name',
                      field_name='name',
                      lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
