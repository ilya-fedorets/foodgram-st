from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "favorites_count",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email",)

    def favorites_count(self, obj):
        return obj.favorite_recipes.count()

    favorites_count.short_description = "Избранных рецептов"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "author__username",
        "author__email",
    )
    list_filter = (
        "user",
        "author",
    )
    autocomplete_fields = ("user", "author")
