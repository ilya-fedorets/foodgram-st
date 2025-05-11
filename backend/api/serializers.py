from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64
import six
from rest_framework import (
    serializers,
)

from recipes.models import (
    Ingredient,
    Recipe,
    IngredientInRecipe,
)
from users.models import Follow
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import (
    NotAuthenticated,
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if "data:" in data and ";base64," in data:
                header, data = data.split(";base64,")
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_image")
            file_name = (
                "uploaded_image.png"
            )
            data = ContentFile(decoded_file, name=file_name)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class CustomUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = (
            "id",
            "is_subscribed",
            "avatar",
        )

    def to_representation(self, instance):
        if isinstance(instance, AnonymousUser) or not getattr(
            instance, "id", None
        ):
            raise NotAuthenticated(
                "Authentication credentials were not provided."
            )
        return super().to_representation(instance)

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if (
            not request
            or not hasattr(request, "user")
            or request.user.is_anonymous
            or isinstance(obj, AnonymousUser)
        ):
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    Поля id, name, measurement_unit являются read-only.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class IngredientAmountWriteSerializer(serializers.Serializer):
    """
    Сериализатор для записи ингредиентов в рецепт (id и количество).
    Используется для write_only поля в RecipeSerializer.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={"min_value": "Количество должно быть не меньше 1."},
    )

    class Meta:
        pass


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения ингредиентов в составе рецепта.
    Показывает id, name, measurement_unit из связанного Ingredient и amount.
    """

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    recipe_ingredients = IngredientInRecipeReadSerializer(
        many=True, read_only=True, source="ingredient_amounts"
    )
    ingredients = IngredientAmountWriteSerializer(many=True, write_only=True)

    image = (
        Base64ImageField()
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "recipe_ingredients",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "id",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if self.partial:
            required_fields_for_patch = {
                "ingredients",
                "name",
                "text",
                "cooking_time",
            }
            sent_fields = set(self.initial_data.keys())
            missing_for_patch = required_fields_for_patch - sent_fields

            if missing_for_patch:
                errors = {
                    field: ["This field is required for update."]
                    for field in missing_for_patch
                }
                raise serializers.ValidationError(errors)
        else:
            if (
                "image" not in self.initial_data and not self.instance
            ):
                raise serializers.ValidationError(
                    {"image": ["This field is required."]}
                )
            elif (
                "image" not in self.initial_data
                and self.instance
                and self.context["request"].method == "PUT"
            ):
                raise serializers.ValidationError(
                    {"image": ["This field is required for PUT."]}
                )
            if "ingredients" not in self.initial_data:
                raise serializers.ValidationError(
                    {"ingredients": ["This field is required."]}
                )
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ingredients"] = IngredientInRecipeReadSerializer(
            instance.ingredient_amounts.all(), many=True, context=self.context
        ).data
        if (
            "recipe_ingredients" in representation
        ):
            representation.pop("recipe_ingredients")
        return representation

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return obj.in_shopping_carts_of.filter(user=request.user).exists()

    def _manage_ingredients(self, recipe, ingredients_data_list):
        IngredientInRecipe.objects.filter(recipe=recipe).delete()
        ings_to_create = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item_data["id"],
                amount=item_data["amount"],
            )
            for item_data in ingredients_data_list
        ]
        IngredientInRecipe.objects.bulk_create(ings_to_create)

    def create(self, validated_data):
        ingredients_list = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self._manage_ingredients(recipe, ingredients_list)
        return recipe

    def update(self, instance, validated_data):
        ingredients_list = validated_data.pop("ingredients", None)
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get(
            "image", instance.image
        )
        instance.save()

        if ingredients_list is not None:
            self._manage_ingredients(instance, ingredients_list)
        return instance

    def validate_ingredients(
        self, data
    ):
        if not data:
            raise serializers.ValidationError(
                "Пожалуйста, укажите ингредиенты."
            )
        ids = [item["id"].id for item in data]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )
        return data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Урезанный сериализатор для рецепта.
    Используется для ответов при добавлении в избранное/список покупок.
    Поля: id, name, image, cooking_time.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class UserWithRecipesSerializer(
    CustomUserSerializer
):
    """
    Сериализатор для пользователя с его рецептами (урезанными).
    Используется для эндпоинта подписок.
    """

    recipes = RecipeMinifiedSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(
        CustomUserSerializer.Meta
    ):
        fields = CustomUserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )
        read_only_fields = CustomUserSerializer.Meta.read_only_fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit_str = self.context.get("request").query_params.get(
            "recipes_limit"
        )
        if recipes_limit_str:
            try:
                recipes_limit = int(recipes_limit_str)
                limited_recipes_qs = instance.recipes.all()[:recipes_limit]
                representation["recipes"] = RecipeMinifiedSerializer(
                    limited_recipes_qs, many=True
                ).data
            except ValueError:
                pass
        return representation


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ("avatar",)


class SetAvatarResponseSerializer(serializers.Serializer):
    avatar = serializers.URLField(read_only=True)

    class Meta:
        fields = ("avatar",)


class RecipeGetShortLinkSerializer(serializers.Serializer):
    short_link = serializers.URLField(
        read_only=True, source="get_short_link"
    )

    class Meta:
        fields = ("short_link",)
