from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class TipoPerfil(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        OPERADOR = 'OPERADOR', 'Operador'
        JOGADOR = 'JOGADOR', 'Jogador'
        
    REQUIRED_FIELDS = ['email', 'cpf', 'data_nascimento']

    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    tipo_perfil = models.CharField(
        max_length=10, choices=TipoPerfil.choices, default=TipoPerfil.JOGADOR
    )

    def __str__(self):
        return self.get_full_name() or self.username


class Participante(models.Model):
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name='participantes')
    usuario_vinculado = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='participacoes'
    )
    nome_completo = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.nome_completo} ({self.reserva})'


class Arena(models.Model):
    nome = models.CharField(max_length=100)
    capacidade_maxima = models.PositiveIntegerField()
    valor_locacao = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nome


class Equipamento(models.Model):
    class Categoria(models.TextChoices):
        MARCADOR = 'MARCADOR', 'Marcador'
        PROTECAO = 'PROTECAO', 'Equipamento de Proteção'
        ACESSORIO = 'ACESSORIO', 'Acessório'

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    quantidade_estoque = models.PositiveIntegerField(default=0)
    valor_locacao = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nome


class Reserva(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='reservas')
    arena = models.ForeignKey(Arena, on_delete=models.PROTECT, related_name='reservas')
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario} - {self.arena} ({self.data_hora_inicio:%d/%m/%Y %H:%M})'


class ReservaEquipamento(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='itens_equipamento')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.PROTECT)
    quantidade_alugada = models.PositiveIntegerField()
    valor_unitario_no_momento = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.quantidade_alugada}x {self.equipamento} (Reserva #{self.reserva_id})'


class TermoAssinatura(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT)
    hash_assinatura = models.CharField(max_length=64)
    caminho_pdf = models.FileField(upload_to='termos/')
    codigo_qr = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    ip_assinatura = models.GenericIPAddressField(null=True, blank=True)
    assinado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Termo - {self.usuario} ({self.assinado_em:%d/%m/%Y})'