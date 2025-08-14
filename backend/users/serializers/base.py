from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

MAX_NAME_LENGTH = 150

User = get_user_model()


class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Некорректные учетные данные')

        if not user.check_password(password):
            raise serializers.ValidationError('Некорректные учетные данные')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        token, _ = Token.objects.get_or_create(user=validated_data['user'])
        return {'auth_token': token.key}


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=MAX_NAME_LENGTH,
    )
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
