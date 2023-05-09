from django.contrib import admin

from .models import Carts, Favorites, Ingredient, IngredientAmount, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('^name',)


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    fk_name = 'recipe'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorited')
    list_filter = ('author', 'name', 'tags')
    exclude = ('ingredients',)
    search_fields = ('^name',)

    inlines = [
        IngredientAmountInline,
    ]

    @admin.display(empty_value='Никто')
    def favorited(self, obj):
        return Favorites.objects.filter(recipe=obj).count()

    favorited.short_description = 'Кол-во людей добавивших в избранное'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorites, FavoriteAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Carts, ShoppingCartAdmin)
admin.site.register(Recipe, RecipeAdmin)
