import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Recipe, IngredientInRecipe
from ingredients.models import Ingredient
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if 'base64,' in data:
                _, data = data.split('base64,', 1)
            try:
                decoded = base64.b64decode(data)
            except Exception:
                raise serializers.ValidationError('Некорректный base64.')
            ext = imghdr.what(None, decoded) or 'jpg'
            file_name = f'{uuid.uuid4().hex}.{ext}'
            data = ContentFile(decoded, name=file_name)
        return super().to_internal_value(data)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeMiniFieldSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        request = self.context.get('request')
        try:
            url = obj.image.url
        except Exception:
            return ''
        return request.build_absolute_uri(url) if request else url


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        a = getattr(user, 'is_authenticated', False)
        return (
            a and obj.favorited_by.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        a = getattr(user, 'is_authenticated', False)
        return (
            a and obj.in_carts.filter(user=user).exists()
        )

    def get_image(self, obj):
        request = self.context.get('request')
        try:
            url = obj.image.url
        except Exception:
            return ''
        return request.build_absolute_uri(url) if request else url


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(), allow_empty=False
        ),
        write_only=True,
        help_text='[{"id": <ingredient_id>, "amount": <int>}, ...]'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True,
        help_text='Список id тегов',
    )
    image = Base64ImageField(
        write_only=True,
        required=True,
        allow_null=True,
        help_text='Изображение в Base64',
    )
    name = serializers.CharField(max_length=256)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        help_text='Время приготовления в минутах (>=1)',
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                _('Нужен хотя бы один ингредиент.')
            )
        seen = set()
        for item in value:
            iid = item.get('id')
            amt = item.get('amount', 0)
            if iid in seen:
                raise serializers.ValidationError(
                    _('Ингредиенты должны быть уникальны.')
                )
            if amt < 1:
                raise serializers.ValidationError(
                    _('Количество должно быть >= 1.')
                )
            if not Ingredient.objects.filter(pk=iid).exists():
                raise serializers.ValidationError(
                    _(f'Ингредиент с id={iid} не найден.')
                )
            seen.add(iid)
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                "Нужно указать хотя бы один тег."
            )
        ids = [tag.id for tag in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Теги должны быть уникальны."
            )
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image_data = validated_data.pop('image', None)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        for item in ingredients_data:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
        if image_data is not None:
            recipe.image = image_data
        recipe.save()
        return recipe

    def validate(self, attrs):
        if self.instance:
            if 'ingredients' not in self.initial_data:
                raise serializers.ValidationError({
                    'ingredients': 'Нужно указать ингредиенты.'
                })
            if 'tags' not in self.initial_data:
                raise serializers.ValidationError({
                    'tags': 'Нужно указать теги.'
                })
        return super().validate(attrs)

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        image_data = validated_data.pop('image', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            IngredientInRecipe.objects.filter(recipe=instance).delete()
            for item in ingredients_data:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient_id=item['id'],
                    amount=item['amount']
                )

        if image_data is not None:
            instance.image = image_data

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data
