from django.contrib.auth import get_user_model
from rest_framework import serializers

from .base import UserSerializer
from recipes.serializers import RecipeMiniFieldSerializer

User = get_user_model()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        qs = obj.recipes.all()
        if limit:
            qs = qs[:int(limit)]
        return RecipeMiniFieldSerializer(
            qs,
            many=True,
            context=self.context,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
