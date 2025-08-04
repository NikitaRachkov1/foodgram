from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Subscription
from recipes.pagination import PageNumberLimitPagination
from .serializers import (CustomUserCreateSerializer, SetAvatarSerializer,
                          SetPasswordSerializer,
                          UserSerializer, UserWithRecipesSerializer)

User = get_user_model()


class ObtainEmailAuthToken(APIView):
    """
    POST /api/auth/token/login/
    Тело: { "email": "...", "password": "..." }
    Ответ 200: { "auth_token": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if email is None or password is None:
            return Response(
                {"errors": "Требуются поля email и password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"errors": "Неверные учётные данные"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"errors": "Неверные учётные данные"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"auth_token": token.key},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberLimitPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_permissions(self):
        if self.action in (
            'me', 'subscriptions', 'subscribe',
            'set_avatar', 'delete_avatar',
            'set_password', 'logout',
        ):
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action in ('subscribe', 'subscriptions'):
            return UserWithRecipesSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        authors = request.user.subscriptions.all()
        page = self.paginate_queryset(authors)
        if page is not None:
            ser = UserWithRecipesSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(ser.data)
        ser = UserWithRecipesSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(ser.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        me = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if me == author:
                return Response(
                    {'detail': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            sub, created = Subscription.objects.get_or_create(
                user=me,
                author=author,
            )
            if not created:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = UserWithRecipesSerializer(
                author,
                context={'request': request}
            ).data
            return Response(data, status=status.HTTP_201_CREATED)

        deleted, _ = Subscription.objects.filter(
            user=me,
            author=author,
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Вы не были подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        permission_classes=[IsAuthenticated],
        parser_classes=[JSONParser],
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def put(self, request):
        ser = SetAvatarSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        request.user.avatar = ser.validated_data['avatar']
        request.user.save()
        return Response(
            {'avatar': request.user.avatar},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        request.user.avatar = ''
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
