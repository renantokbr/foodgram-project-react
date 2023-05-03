from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import relations, serializers, validators
from rest_framework.fields import ReadOnlyField

from api.utils import set_of_ingredients
from recipe.models import (Carts, Favorites, Ingredient, IngredientAmount,
                           Recipe, Tag)
from users.models import Subscriptions, User


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""
    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe'
            )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorites.objects.all(),
                message='Рецепт уже в избранном',
                fields=['recipe', 'user']
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в список покупок."""
    class Meta:
        model = Carts
        fields = (
            'user',
            'recipe'
            )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Carts.objects.all(),
                message='Рецепт уже есть в списке покупок',
                fields=['recipe', 'user']
            )
        ]


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка рецептов в подписках."""
    class Meta:
        model = Recipe
        read_only_fields = ['__all__']
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""
    id = ReadOnlyField(source='author.id')
    email = ReadOnlyField(source='author.email')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count'
            )

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSmallSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_subscribed'
        )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.following.filter(user=request.user).exists())


class FollowSerializer(UserSerializer):
    """Сериализатор списка подписок"""
    class Meta:
        model = Subscriptions
        fields = (
            'user',
            'author'
            )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('user', 'author')
            )
        ]

    def to_representation(self, instance):
        return SubscribeSerializer(instance).data


class UserFollowsSerializer(UserSerializer):
    """Сериализатор пользователей в подписках."""
    recipes = serializers.SerializerMethodField(
        method_name='paginated_recipes'
        )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
        )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
            )
        read_only_fields = ['__all__']

    def get_recipes_count(self, obj: int) -> int:
        return obj.author.recipes.count()

    def get_subscribed(*args) -> bool:
        return True

    def paginated_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.author.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSmallSerializer(recipes, many=True, context=context).data


class GetIngredientsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения ингридиентов."""
    id = ReadOnlyField(source='ingredients.id')
    name = ReadOnlyField(source='ingredients.name')
    measurement_unit = ReadOnlyField(source='ingredients.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
            )


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__']


class SerializerRecipeCookingTime(serializers.ModelSerializer):
    """Сериализатор времени приготовления"""
    class Meta:
        model = Recipe
        fields = (
            'cooking_time',
            )


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов"""
    author = UserSerializer()
    ingredients = GetIngredientsRecipeSerializer(source='ingredient_recipe',
                                                 many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
        )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favorited'
            )

    def _exist(self, model, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(
            user=request.user,
            recipe__id=obj.id
        ).exists()

    def get_is_favorited(self, obj):
        return self._exist(Favorites, obj)

    def get_is_in_shopping_cart(self, obj):
        return self._exist(Carts, obj)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""
    tags = relations.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True,
                                                  source='ingredient_recipe', )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
        )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
            )
        read_only_fields = ('is_favorite', 'is_shopping_cart',)

    def get_ingredients(self, obj: object):
        return obj.ingredients.values('id', 'name', 'measurement_unit',
                                      amount=F('recipe__amount'))

    def _exist(self, model, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return model.objects.filter(user=request.user,
                                        recipe__id=obj.id).exists()

    def get_is_favorited(self, obj):
        return self._exist(Favorites, obj)

    def get_is_in_shopping_cart(self, obj):
        return self._exist(Carts, obj)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо выбрать ингредиенты!')
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1!')

        ids = [ingredient['id'] for ingredient in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                'Данный ингредиент уже есть в рецепте!')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Необходимо выбрать теги!')
        return tags

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0!'
                )
        return data

    def create_tags(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)

    def create_ingredients(self, recipe, ingredients):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(recipe=recipe,
                              ingredients=get_object_or_404(Ingredient,
                                                            pk=ingredient[
                                                                'id']),
                              amount=ingredient['amount'])
             for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredient')

        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            set_of_ingredients(recipe, ingredients)

        recipe.save()
        return recipe
