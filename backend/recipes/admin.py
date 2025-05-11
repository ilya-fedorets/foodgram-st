from django.contrib import admin
from .models import (
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingCart,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    autocomplete_fields = ("ingredient",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "cooking_time",
        "pub_date",
        "favorites_count_list_view",
    )
    search_fields = ("name", "author__username", "text")
    list_filter = ("author", "pub_date")
    inlines = [IngredientInRecipeInline]
    readonly_fields = ("pub_date", "favorites_count_change_view")

    fieldsets = (
        (None, {"fields": ("name", "author", "text", "image")}),
        (
            "Детали рецепта",
            {
                "fields": ("cooking_time",)
            },
        ),
        ("Статистика", {"fields": ("favorites_count_change_view",)}),
        ("Даты", {"fields": ("pub_date",), "classes": ("collapse",)}),
    )

    def favorites_count_list_view(self, obj):
        return obj.favorited_by.count()

    favorites_count_list_view.short_description = "В избранном"

    def favorites_count_change_view(self, obj):
        return obj.favorited_by.count()

    favorites_count_change_view.short_description = "Добавлений в избранное"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    autocomplete_fields = ('user', 'recipe')
