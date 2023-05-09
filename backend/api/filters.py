from django.contrib.auth import get_user_model
from django_filters.rest_framework import (ModelMultipleChoiceFilter,
                                           BooleanFilter, CharFilter,
                                           FilterSet)
from recipe.models import Ingredient, Recipe, Tag


User = get_user_model()


class RecipeFilter(FilterSet):
    """Фильтрация по автору, тэгу, избранному и добавленному в покупки."""
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = CharFilter(method='filter_author')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags',)

    def filter_author(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(**{name: value})
        if value == 'me':
            value = self.request.user.id
            return queryset.filter(**{name: value})
        return queryset

    def _filter_is_param(self, queryset, name, value, param):
        if value and self.request.user.is_authenticated:
            return queryset.filter(**{f'{param}__user': self.request.user})
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._filter_is_param(queryset, name, value, param='favorites')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter_is_param(queryset, name,
                                     value, param='shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(favorite__user=self.request.user)

    def filter_is_in_shopping_cart_1(self, queryset, name, value):
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
