from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Arena, Equipamento, Reserva, ReservaEquipamento, TermoAssinatura
from .serializers import ReservaSerializer
from .services import gerar_pdf_termo, gerar_hash_assinatura


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        arena = serializer.validated_data['arena']
        inicio = serializer.validated_data['data_hora_inicio']
        fim = serializer.validated_data['data_hora_fim']
        itens_equipamento = serializer.validated_data.pop('itens_equipamento', [])

        with transaction.atomic():
            # 1. Trava e valida a Arena
            Arena.objects.select_for_update().get(pk=arena.pk)

            conflito_arena = Reserva.objects.filter(
                arena=arena,
                status__in=[Reserva.Status.PENDENTE, Reserva.Status.CONFIRMADA],
                data_hora_inicio__lt=fim,
                data_hora_fim__gt=inicio,
            ).exists()

            if conflito_arena:
                return Response(
                    {'detail': 'Essa arena já está reservada nesse horário.'},
                    status=status.HTTP_409_CONFLICT,
                )

            # 2. Trava os equipamentos pedidos, em ordem fixa por PK.
            #    Ordem fixa evita deadlock: se duas reservas pedem os mesmos
            #    dois equipamentos em ordens diferentes, sem isso o Postgres
            #    pode travar as duas esperando uma a outra pra sempre.
            equipamento_ids = sorted(item['equipamento'].pk for item in itens_equipamento)
            equipamentos_travados = {
                eq.pk: eq for eq in
                Equipamento.objects.select_for_update().filter(pk__in=equipamento_ids)
            }

            for item in itens_equipamento:
                equipamento = equipamentos_travados[item['equipamento'].pk]
                quantidade_pedida = item['quantidade_alugada']

                quantidade_ja_alugada = ReservaEquipamento.objects.filter(
                    equipamento=equipamento,
                    reserva__status__in=[Reserva.Status.PENDENTE, Reserva.Status.CONFIRMADA],
                    reserva__data_hora_inicio__lt=fim,
                    reserva__data_hora_fim__gt=inicio,
                ).aggregate(total=Sum('quantidade_alugada'))['total'] or 0

                disponivel = equipamento.quantidade_estoque - quantidade_ja_alugada

                if quantidade_pedida > disponivel:
                    return Response(
                        {'detail': f'Estoque insuficiente de "{equipamento.nome}" nesse horário. Disponível: {disponivel}.'},
                        status=status.HTTP_409_CONFLICT,
                    )

            # 3. Cria a reserva e os itens, só depois de tudo validado
            reserva = Reserva.objects.create(
                usuario=serializer.validated_data['usuario'],
                arena=arena,
                data_hora_inicio=inicio,
                data_hora_fim=fim,
            )

            for item in itens_equipamento:
                equipamento = equipamentos_travados[item['equipamento'].pk]
                ReservaEquipamento.objects.create(
                    reserva=reserva,
                    equipamento=equipamento,
                    quantidade_alugada=item['quantidade_alugada'],
                    valor_unitario_no_momento=equipamento.valor_locacao,
                )

        output_serializer = self.get_serializer(reserva)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def assinar_termo(self, request, pk=None):
        reserva = self.get_object()

        if reserva.status == Reserva.Status.CANCELADA:
            return Response(
                {'detail': 'Não é possível assinar termo de uma reserva cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(reserva, 'termoassinatura'):
            return Response(
                {'detail': 'Essa reserva já possui um termo assinado.'},
                status=status.HTTP_409_CONFLICT,
            )

        ip = request.META.get('REMOTE_ADDR')
        buffer_pdf = gerar_pdf_termo(reserva)
        hash_assinatura = gerar_hash_assinatura(reserva, ip)

        termo = TermoAssinatura(
            usuario=reserva.usuario,
            reserva=reserva,
            hash_assinatura=hash_assinatura,
            ip_assinatura=ip,
        )
        termo.caminho_pdf.save(
            f'termo_reserva_{reserva.id}.pdf',
            ContentFile(buffer_pdf.read()),
            save=True,
        )

        return Response(
            {
                'detail': 'Termo assinado com sucesso.',
                'termo_id': termo.id,
                'pdf_url': termo.caminho_pdf.url,
                'hash_assinatura': termo.hash_assinatura,
            },
            status=status.HTTP_201_CREATED,
        )