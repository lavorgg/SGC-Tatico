from rest_framework import serializers
from .models import Reserva, ReservaEquipamento
from .models import Arena, Equipamento, Reserva, ReservaEquipamento

class ArenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arena
        fields = ['id', 'nome', 'capacidade_maxima', 'valor_locacao']


class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = ['id', 'nome', 'categoria', 'quantidade_estoque', 'valor_locacao']


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