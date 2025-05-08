from django.db import models
from django.core.validators import MinValueValidator
from core.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)

    class Meta:
        unique_together = ('name', 'measurement_unit')
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/images/')
    cooking_time = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} by {self.author.username}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_links')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_links')
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.ingredient.name} x{self.amount} for {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} -> ♥ {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='in_carts')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} -> 🛒 {self.recipe.name}'
