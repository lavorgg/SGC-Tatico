from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Arena, Equipamento, Reserva, ReservaEquipamento, TermoAssinatura


class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados do SGC-Tático', {'fields': ('cpf', 'data_nascimento', 'tipo_perfil')}),
    )

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Arena)
admin.site.register(Equipamento)
admin.site.register(Reserva)
admin.site.register(ReservaEquipamento)
admin.site.register(TermoAssinatura)