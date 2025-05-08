from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Recipe, Favorite, ShoppingCart, Ingredient
from recipes.serializers import RecipeSerializer, ShortRecipeSerializer, IngredientSerializer
from core.pagination import StandardPagination


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        author = self.request.query_params.get('author')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_cart = self.request.query_params.get('is_in_shopping_cart')

        if author:
            queryset = queryset.filter(author__id=author)

        if user.is_authenticated:
            if is_favorited == '1':
                queryset = queryset.filter(favorited_by__user=user)
            if is_in_cart == '1':
                queryset = queryset.filter(in_carts__user=user)

        return queryset

    def _toggle(self, model, user, recipe, create_serializer=ShortRecipeSerializer):
        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            return Response({'error': 'Уже добавлено'}, status=400)
        return Response(create_serializer(recipe).data, status=201)

    def _untoggle(self, model, user, recipe):
        deleted = model.objects.filter(user=user, recipe=recipe).delete()
        if deleted[0] == 0:
            return Response({'error': 'Не найдено'}, status=404)
        return Response(status=204)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self._toggle(Favorite, request.user, recipe)
        return self._untoggle(Favorite, request.user, recipe)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self._toggle(ShoppingCart, request.user, recipe)
        return self._untoggle(ShoppingCart, request.user, recipe)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        ingredients = {}
        recipes = set()

        for item in ShoppingCart.objects.filter(user=request.user).select_related('recipe'):
            recipes.add(item.recipe.name)
            for ing in item.recipe.ingredient_links.all():
                key = (ing.ingredient.name, ing.ingredient.measurement_unit)
                ingredients[key] = ingredients.get(key, 0) + ing.amount

        lines = [f'Список покупок на {timezone.now().date()}:\n']
        for i, ((name, unit), amount) in enumerate(sorted(ingredients.items()), 1):
            lines.append(f'{i}. {name.capitalize()} ({unit}) — {amount}')

        lines.append('\nРецепты:')
        for j, name in enumerate(sorted(recipes), 1):
            lines.append(f'{j}. {name}')

        content = '\n'.join(lines)
        return HttpResponse(content, content_type='text/plain')

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        return Response({'short-link': f'https://localhost/recipes/{pk}'})


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None  # отключим пагинацию

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset
