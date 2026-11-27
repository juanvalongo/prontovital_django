from django.conf import settings
from django.db import models
from django.db.models import Q

from .agenda import PROFISSIONAL_CHOICES


class Paciente(models.Model):
    SEXO_CHOICES = [
        ("Masculino", "Masculino"),
        ("Feminino", "Feminino"),
        ("Outro", "Outro"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_paciente",
    )
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=11)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.email


class Consulta(models.Model):
    STATUS_AGENDADO = "agendado"
    STATUS_CANCELADO = "cancelado"
    STATUS_CHOICES = [
        (STATUS_AGENDADO, "Agendado"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="consultas",
    )
    data = models.DateField()
    horario = models.TimeField()
    profissional = models.CharField(max_length=40, choices=PROFISSIONAL_CHOICES)
    especialidade = models.CharField(max_length=100)
    clinica = models.CharField(max_length=120)
    observacao = models.TextField(blank=True)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_AGENDADO,
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data", "horario"]
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        constraints = [
            models.UniqueConstraint(
                fields=["data", "horario", "profissional"],
                condition=Q(status="agendado"),
                name="unique_active_professional_slot",
            ),
        ]

    def __str__(self):
        return f"{self.data:%d/%m/%Y} às {self.horario:%H:%M}"
