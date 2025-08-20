from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Recipe, ShoppingCart, ShortLink
from .pagination import PageNumberLimitPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (RecipeCreateUpdateSerializer,
                          RecipeListSerializer,
                          RecipeMiniFieldSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для REST API рецептов:
    - GET /api/recipes/                список с фильтрацией и пагинацией
    - POST /api/recipes/               создание рецепта
    - GET /api/recipes/{id}/           получение детали рецепта
    - PATCH/PUT /api/recipes/{id}/     частичное/полное обновление
    - DELETE /api/recipes/{id}/        удаление рецепта
    - POST/DELETE /api/recipes/{id}/favorite/        избранное
    - POST/DELETE /api/recipes/{id}/shopping_cart/  список покупок
    - GET  /api/recipes/{id}/get-link/               получение короткой ссылки
    - GET  /api/recipes/download_shopping_cart/      файл списка покупок
    """
    queryset = (
        Recipe.objects.all().order_by('-id')
        .select_related('author')
        .prefetch_related('tags', 'ingredients')
        .distinct()
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PageNumberLimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateUpdateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        out = RecipeListSerializer(recipe, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Недостаточно прав для изменения этого рецепта.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = RecipeCreateUpdateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save()
        out = RecipeListSerializer(recipe, context={'request': request})
        return Response(out.data)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            return Response(
                {'detail': 'Недостаточно прав для удаления этого рецепта'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """
        POST   /api/recipes/{id}/favorite/  → добавить в избранное, вернуть
        RecipeMiniField + 201
        DELETE /api/recipes/{id}/favorite/  → удалить, вернуть 204
        """
        recipe = self.get_object()
        if request.method == 'POST':
            fav, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe,
            )
            if not created:
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = RecipeMiniFieldSerializer(
                recipe,
                context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)
        deleted, _ = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            cart, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if not created:
                return Response(
                    {'detail': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = RecipeMiniFieldSerializer(
                recipe, context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)

        deleted, _ = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Рецепта не было в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short, _ = ShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={
                'short_url': request.build_absolute_uri(
                    f'/recipes/{recipe.pk}'
                )
            },
        )
        return Response(
            {'short-link': short.short_url}, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = {}
        for cart in ShoppingCart.objects.filter(user=request.user):
            for ingr in cart.recipe.ingredients.all():
                key = (ingr.ingredient.name, ingr.ingredient.measurement_unit)
                ingredients[key] = ingredients.get(key, 0) + ingr.amount
        lines = [
            f"{name} ({unit}) — {amt}"
            for (name, unit), amt in ingredients.items()
        ]
        txt = "\n".join(lines)
        resp = HttpResponse(txt, content_type="text/plain")
        resp["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return resp
