from rest_framework import serializers
from .models import User, Team
from django.contrib.auth.hashers import make_password
from .models import Task


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField(read_only=True)  # Show members

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'created_by', 'members']
        read_only_fields = ['created_by']

    def get_members(self, obj):
        return [
            {"id": member.id, "username": member.username, "role": member.role}
            for member in obj.members.all()
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'teams']
        extra_kwargs = {
            'password': {'write_only': True},
            'teams': {'required': True}
        }

    def validate_teams(self, value):
        if not value:
            raise serializers.ValidationError("User must be assigned to at least one team.")
        return value

    def create(self, validated_data):
        teams = validated_data.pop('teams')
        validated_data['password'] = make_password(validated_data['password'])
        user = super().create(validated_data)
        user.teams.set(teams)
        return user

    def update(self, instance, validated_data):
        teams = validated_data.pop('teams', None)
        if teams is not None:
            if not teams:
                raise serializers.ValidationError("User must belong to at least one team.")
            instance.teams.set(teams)
        return super().update(instance, validated_data)

class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    last_updated_by = serializers.ReadOnlyField(source='last_updated_by.username')
    assigned_to_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 
            'created_by', 'last_updated_by',
            'assigned_to', 'assigned_to_details',
            'due_date', 'completed',
            'created_at', 'updated_at'
        ]

    def get_assigned_to_details(self, obj):
        return [{"id": user.id, "username": user.username, "role": user.role} for user in obj.assigned_to.all()]

    def validate_assigned_to(self, value):
        if not value:
            raise serializers.ValidationError("Task must be assigned to at least one user.")
        return value

    def create(self, validated_data):
        assigned_users = validated_data.pop('assigned_to')
        task = Task.objects.create(**validated_data)
        task.assigned_to.set(assigned_users)
        return task

    def update(self, instance, validated_data):
        assigned_users = validated_data.pop('assigned_to', None)
        if assigned_users is not None:
            instance.assigned_to.set(assigned_users)
        return super().update(instance, validated_data)
