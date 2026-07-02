from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReservaViewSet, ArenaViewSet, EquipamentoViewSet, ValidarTermoView

router = DefaultRouter()
router.register('reservas', ReservaViewSet)
router.register('arenas', ArenaViewSet)
router.register('equipamentos', EquipamentoViewSet)

urlpatterns = router.urls + [
    path('termos/validar/<str:hash_assinatura>/', ValidarTermoView.as_view(), name='validar-termo'),
]