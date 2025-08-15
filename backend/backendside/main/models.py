from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='teams_created'
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    teams = models.ManyToManyField(Team, related_name='members', blank=False)

    # Override groups & permissions to prevent clash
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='tasks_created'
    )
    last_updated_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_updated'
    )

    assigned_to = models.ManyToManyField(
        'User',
        related_name='tasks_assigned'
    )

    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)  # when created
    updated_at = models.DateTimeField(auto_now=True)      # when modified

    def __str__(self):
        return f"{self.title} - {'Completed' if self.completed else 'Pending'}"

    class Meta:
        ordering = ['-created_at']
