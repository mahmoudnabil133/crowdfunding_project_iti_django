from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User, Project


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile_phone',)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'total_target', 'start_date', 'end_date')
