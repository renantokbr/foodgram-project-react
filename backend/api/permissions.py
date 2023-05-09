from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly

AllowAny = permissions.AllowAny
IsAuthenticated = permissions.IsAuthenticated


class AuthorOrAdmin(IsAuthenticatedOrReadOnly):
    """Доступ к изменению контента автору и администратору."""
    message = 'Редактирование доступно только автору или администратору'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj
                or obj.author == request.user)
