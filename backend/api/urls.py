from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientView, RecipeView, TagView, UserView

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagView, 'tags')
router.register('ingredients', IngredientView, 'ingredients')
router.register('recipes', RecipeView, 'recipes')
router.register('users', UserView, 'users')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
