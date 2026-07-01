from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet, ValidarTermoView

router = DefaultRouter()
router.register('reservas', ReservaViewSet)

urlpatterns = router.urls + [
    path('termos/validar/<str:hash_assinatura>/', ValidarTermoView.as_view(), name='validar-termo'),
]