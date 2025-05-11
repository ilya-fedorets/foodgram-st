import django_filters
from recipes.models import (
    Recipe,
    Ingredient,
)

from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, CharFilter

User = get_user_model()


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ["author"]


class IngredientFilter(FilterSet):
    """
    Фильтр для ингредиентов.
    Позволяет фильтровать по частичному вхождению в начале названия.
    """

    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
