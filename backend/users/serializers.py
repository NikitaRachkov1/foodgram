from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import serializers

User = get_user_model()


class CustomUserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(pk=user.pk).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        from recipes.serializers import RecipeMiniFieldSerializer
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


class SetAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()


class SetAvatarResponseSerializer(serializers.Serializer):
    avatar = serializers.URLField()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError('Неверный текущий пароль!')
        return value
