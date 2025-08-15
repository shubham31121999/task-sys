from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Team, Task

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Task)
