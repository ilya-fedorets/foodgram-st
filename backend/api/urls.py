from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    UserSubscriptionViewSet,
    UserAvatarView,
)  # Добавил UserAvatarView

app_name = "api"

router_v1 = DefaultRouter()

router_v1.register(r"ingredients", IngredientViewSet, basename="ingredients")
router_v1.register(r"recipes", RecipeViewSet, basename="recipes")
router_v1.register(
    r"users", UserSubscriptionViewSet, basename="user-subscriptions"
)

urlpatterns = [
    path("", include(router_v1.urls)),
    path("users/me/avatar/", UserAvatarView.as_view(), name="user-me-avatar"),
]
