from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import User, Team ,Task
from .serializers import UserSerializer, TeamSerializer ,TaskSerializer

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superuser'

class IsManagerOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['manager', 'superuser']


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsManagerOrSuperUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return User.objects.filter(teams__in=user.teams.all()).distinct()
        return super().get_queryset()

    def perform_create(self, serializer):
        current_user = self.request.user
        new_user_role = self.request.data.get('role')

        if current_user.role == 'manager':
            if new_user_role != 'user':
                raise PermissionDenied("Managers can only create Users, not Managers.")

            teams = self.request.data.get('teams', [])
            for team_id in teams:
                if not current_user.teams.filter(id=team_id).exists():
                    raise PermissionDenied("Managers can only assign users to their own teams.")

        serializer.save()


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()
    permission_classes = [IsManagerOrSuperUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsManagerOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'manager':
            return Task.objects.filter(
                assigned_to__in=user.teams.all().values_list('members', flat=True)
            ).distinct()
        elif user.role == 'user':
            return Task.objects.filter(assigned_to=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user)
