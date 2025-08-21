from django_filters import rest_framework as filters

from .models import Recipe
from tags.models import Tag


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

    def filter_tags(self, qs, name, value):
        params = self.request.query_params
        tags_params_check = ('tags' in params) or (value is not None)

        raw_values = params.getlist('tags')
        if not raw_values and value:
            raw_values = [value]

        values = []
        for value in raw_values:
            if value:
                parts = [part.strip() for part in value.split(',')]
                values.extend([part for part in parts if part])

        if not tags_params_check:
            return qs

        if not values:
            return qs

        all_slugs = set(Tag.objects.values_list('slug', flat=True))
        valid_slugs = sorted(set(v for v in values if v in all_slugs))

        if not valid_slugs:
            return qs.none()

        if set(valid_slugs) == all_slugs and all_slugs:
            return qs

        return qs.filter(tags__slug__in=valid_slugs).distinct()
