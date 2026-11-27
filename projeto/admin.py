from django.contrib import admin
from .models import Consulta, Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cidade", "estado")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name")


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("data", "horario", "profissional", "paciente", "status")
    list_filter = ("status", "data", "especialidade")
    search_fields = ("paciente__usuario__email", "paciente__usuario__first_name")
