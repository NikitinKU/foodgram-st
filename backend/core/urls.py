from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import CustomUserViewSet
from recipes.views import RecipeViewSet
from recipes.views import RecipeViewSet, IngredientViewSet

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
