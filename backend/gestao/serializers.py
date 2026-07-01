from rest_framework import serializers
from .models import Reserva, ReservaEquipamento


class ReservaEquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaEquipamento
        fields = ['equipamento', 'quantidade_alugada']


class ReservaSerializer(serializers.ModelSerializer):
    itens_equipamento = ReservaEquipamentoSerializer(many=True, required=False)

    class Meta:
        model = Reserva
        fields = ['id', 'usuario', 'arena', 'data_hora_inicio', 'data_hora_fim', 'status', 'criado_em', 'itens_equipamento']
        read_only_fields = ['status', 'criado_em']