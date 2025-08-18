from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, qs, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return qs.filter(favorited_by__user=user)
        return qs

    def filter_is_in_shopping_cart(self, qs, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return qs.filter(in_carts__user=user)
        return qs
