from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import (decorators, exceptions, mixins, response, status,
                            viewsets)

from recipe import models as models_recipe
from users import models as models_user

from . import filters, paginators, permissions, serializers

User = get_user_model()


class PaginateResponse:
    """
    Add a paginate response.
    """
    def paginate_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_200_OK)


class UserViewSet(PaginateResponse,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Управление пользователями"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = paginators.Pagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return serializers.UserSerializer
        elif self.action in ('create',):
            return serializers.UsersCreateSerializer
        elif self.action in ('subscribe',):
            return serializers.SubscriptionCreateSerializer
        elif self.action in ('subscriptions',):
            return serializers.SubscriberGetSerializer
        elif self.action in ('set_password',):
            return serializers.UsersChangePasswordSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_anonymous or self.action not in ('list',
                                                                 'retrieve'):
            return context

        data = {'subscriber': self.get_user()}
        if self.kwargs:
            data['author'] = self.get_object()

        add_context_data = {
            'subscribed_users': models_user.Subscriptions,
        }
        for name, model in add_context_data.items():
            context[name] = set(
                model.objects.filter(**data).values_list('author_id',
                                                         flat=True))
        return context

    def get_user(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        if self.get_user() == self.get_object():
            return self.me(request, *args, **kwargs)
        return super().retrieve(request, *args, **kwargs)

    @decorators.action(
        methods=['get'], detail=False, url_path='me', url_name='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        instance = self.get_user()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return response.Response(data=serializer.data,
                                 status=status.HTTP_200_OK,
                                 headers=headers)

    @decorators.action(
        methods=['post'], detail=False, url_path='set_password',
        url_name='set_password',
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['post', 'delete'], detail=True, url_path='subscribe',
        url_name='subscribe',
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        data = {
            'subscriber': self.get_user().id,
            'author': self.get_object().id
        }
        if self.request.method == 'POST':
            return self._create_subscribe(data)
        elif self.request.method == 'DELETE':
            return self._delete_subscribe(data)

    def _create_subscribe(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def _delete_subscribe(self, data):
        serializer = self.get_serializer()
        serializer.delete(data)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['get'], detail=False, url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=paginators.Pagination
    )
    def subscriptions(self, request, *args, **kwargs):
        instance = self.get_user()
        subscriptions = instance.subscriber.all()
        subscribers = User.objects.filter(
            id__in=subscriptions.values('author'),
        )
        return self.paginate_response(subscribers)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Управление тегами"""
    queryset = models_recipe.Tag.objects.all()
    serializer_class = serializers.TagGetSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Управление ингредиентами"""
    queryset = models_recipe.Ingredient.objects.all()
    serializer_class = serializers.IngredientGetSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filterset_class = filters.IngredientFilter


class RecipeViewSet(PaginateResponse, viewsets.ModelViewSet):
    """Управление рецептами"""
    queryset = models_recipe.Recipe.objects.all()
    permission_classes = (permissions.AuthorOrAdmin,)
    filterset_class = filters.RecipeFilter

    def get_user(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeGetSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return serializers.RecipeCreateSerializer
        elif self.action in ('favorite',):
            return serializers.FavoriteCreateSerializer
        elif self.action in ('shopping_cart',):
            return serializers.ShoppingCreateSerializer
        elif self.action in ('download_shopping_cart',):
            return serializers.ShoppingCartDownloadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_anonymous or self.action not in ('list',
                                                                 'retrieve'):
            return context

        data = {'user': self.get_user()}
        if self.kwargs:
            data['recipe'] = self.get_object()

        add_context_data = {
            'favorite_recipes': models_recipe.Favorites,
            'shopping_recipes': models_recipe.Carts
        }
        for name, model in add_context_data.items():
            context[name] = set(model.objects.filter(**data).values_list(
                'recipe_id', flat=True)
                )

        data = {
            'subscriber': self.get_user(),
        }
        if self.kwargs:
            data['author_id'] = self.get_object().author

        context['subscribed_users'] = (
            set(models_user.Subscriptions.objects.filter(**data).values_list(
                'author_id', flat=True))
            )
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.get_user())

    def perform_update(self, serializer):
        serializer.save(author=self.get_user())

    @decorators.action(
        methods=['delete', 'post'],
        detail=True, url_path='favorite', url_name='favorite',
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        return self._favorite_or_shopping_cart_view()

    @decorators.action(
        methods=['delete', 'post'],
        detail=True, url_path='shopping_cart', url_name='shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, *args, **kwargs):
        return self._favorite_or_shopping_cart_view()

    def _favorite_or_shopping_cart_view(self):
        data = {
            'user': self.get_user().id,
            'recipe': self.get_object().id
        }
        if self.request.method == 'POST':
            return self._create_instance(data)
        if self.request.method == 'DELETE':
            return self._delete_instance(data)

    def _create_instance(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)

    def _delete_instance(self, data):
        serializer = self.get_serializer()
        serializer.delete(data)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['get'], detail=False,
        url_path='download_shopping_cart', url_name='download_shopping_cart',
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        user = self.get_user()
        if not user.shopping_cart.exists():
            raise exceptions.ValidationError('В списке покупок нет рецептов.')

        ingredients = models_recipe.IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        filename, shopping_list = self.create_shopping_list(ingredients)

        resp = HttpResponse(shopping_list, content_type='text/plain')
        resp['Content-Disposition'] = f'attachment; filename={filename}'
        return resp

    def create_shopping_list(self, ingredients):
        today = datetime.today()
        user = self.get_user()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'
        filename = f'{user.username}_shopping_list.txt'
        return filename, shopping_list
