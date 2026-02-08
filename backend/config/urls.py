from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import ProcedureViewSet, RuleEvaluationView

router = DefaultRouter()
router.register("procedures", ProcedureViewSet, basename="procedure")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/rules/evaluate/", RuleEvaluationView.as_view(), name="rules-evaluate"),
]
