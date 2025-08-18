from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import IngredientInRecipe, Favorite, Recipe, ShoppingCart


class IngredientRecipeInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        seen = set()
        for form in self.forms:
            if hasattr(form, 'cleaned_data'):
                if form.cleaned_data.get('DELETE'):
                    continue
                ingredient = form.cleaned_data.get('ingredient')
                amount = form.cleaned_data.get('amount')
                if ingredient and amount:
                    if ingredient.pk in seen:
                        form.add_error('ingredient', 'Ингредиент уже добавлен')
                    seen.add(ingredient.pk)
        if len(seen) == 0:
            raise ValidationError('Нужно добавить хотя бы 1 ингредиент')


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'в избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
