from django.contrib import admin
from django.urls import path, include
from accounts.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("rosetta/", include("rosetta.urls")),
    path("admin/", admin.site.urls),
    path("", include("rss.urls", namespace="rss")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("interactions/", include("interactions.urls", namespace="interactions")),
]

# urlpatterns += i18n_patterns()
