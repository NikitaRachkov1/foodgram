from django.contrib import admin

from .models import IngredientInRecipe, Favorite, Recipe, ShoppingCart


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0


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
