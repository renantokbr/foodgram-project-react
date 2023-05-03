from django.db.models import F, Sum
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import decorators, generics, response, status, viewsets

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import Pagination
from api.permissions import AuthorAndAdmin
from api.serializers import (FavoriteSerializer, FollowSerializer,
                             GetRecipeSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartSerializer,
                             SubscribeSerializer, TagSerializer,
                             UserSerializer)
from api.utils import prepare_file
from recipe.models import (Carts, Favorites, Ingredient, IngredientAmount,
                           Recipe, Tag)
from users.models import Subscriptions, User


class UserView(DjoserUserViewSet):
    pagination_class = Pagination

    @decorators.action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, id):
        user = request.user
        author = generics.get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        if request.method == 'POST':
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        generics.get_object_or_404(
            Subscriptions,
            user=request.user,
            author=author
        ).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(methods=('GET',), detail=False)
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscribeSerializer(
                self.paginate_queryset(
                    Subscriptions.objects.filter(user=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )

    @decorators.action(methods=('GET',), detail=False)
    def me(self, request):
        if request.user.is_anonymous:
            return response.Response(status=status.HTTP_401_UNAUTHORIZED)
        return response.Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )


class RecipeView(viewsets.ModelViewSet):
    """Управление рецептами."""
    queryset = Recipe.objects.select_related('author')
    permission_classes = (AuthorAndAdmin,)
    pagination_class = Pagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetRecipeSerializer
        return RecipeSerializer

    @staticmethod
    def create_object(serializers, user, recipe):
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = serializers(
            data=data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_object(request, pk, model):
        generics.get_object_or_404(
            model,
            user=request.user,
            recipe=generics.get_object_or_404(Recipe, id=pk)
        ).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(methods=('POST',), detail=True)
    def favorite(self, request, pk):
        return self.create_object(
            FavoriteSerializer,
            request.user,
            generics.get_object_or_404(Recipe, id=pk)
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(
            request=request,
            pk=pk,
            model=Favorites
        )

    @decorators.action(methods=('POST',), detail=True)
    def shopping_cart(self, request, pk):
        return self.create_object(
            ShoppingCartSerializer,
            request.user,
            generics.get_object_or_404(Recipe, id=pk)
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_object(
            request=request,
            pk=pk,
            model=Carts
        )

    @decorators.action(methods=('GET',), detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')).order_by(
            'ingredient').annotate(sum_amount=Sum('amount'))
        return prepare_file(user, ingredients)


class TagView(viewsets.ReadOnlyModelViewSet):
    """Управление тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AuthorAndAdmin,)
    pagination_class = None


class IngredientView(viewsets.ReadOnlyModelViewSet):
    """Управление ингридиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AuthorAndAdmin,)
    pagination_class = None
    filterset_class = IngredientFilter
