import re
from datetime import date

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.utils import timezone

from .agenda import (
    DATA_FIM,
    DATA_INICIO,
    HORARIOS_VALIDOS,
    PROFISSIONAL_CHOICES,
    PROFISSIONAIS,
    horarios_para_data,
)
from .models import Consulta, Paciente

User = get_user_model()


class CadastroPacienteForm(forms.Form):
    nome = forms.CharField(label="Nome completo", max_length=150)
    email = forms.EmailField(label="E-mail")
    senha = forms.CharField(
        label="Senha",
        min_length=8,
        widget=forms.PasswordInput,
        help_text="Use pelo menos 8 caracteres.",
    )
    confirmar_senha = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput,
    )
    telefone = forms.CharField(label="Telefone com DDD", max_length=15)
    cpf = forms.CharField(label="CPF", max_length=14)
    endereco = forms.CharField(label="Endereço")
    cidade = forms.CharField(label="Cidade", max_length=100)
    estado = forms.RegexField(
        label="Estado (UF)",
        regex=r"^[A-Za-z]{2}$",
        error_messages={"invalid": "Informe a sigla do estado com 2 letras."},
    )
    data_nascimento = forms.DateField(
        label="Data de nascimento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    sexo = forms.ChoiceField(label="Sexo", choices=Paciente.SEXO_CHOICES)
    observacoes = forms.CharField(
        label="Observações médicas (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-input"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Já existe uma conta cadastrada com este e-mail.")
        return email

    def clean_cpf(self):
        cpf = re.sub(r"\D", "", self.cleaned_data["cpf"])
        if len(cpf) != 11:
            raise ValidationError("Informe os 11 dígitos do CPF.")
        if Paciente.objects.filter(cpf=cpf).exists():
            raise ValidationError("Já existe um cadastro com este CPF.")
        return cpf

    def clean_telefone(self):
        telefone = re.sub(r"\D", "", self.cleaned_data["telefone"])
        if len(telefone) not in (10, 11):
            raise ValidationError("Informe um telefone com DDD.")
        return telefone

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data["data_nascimento"]
        if data_nascimento >= timezone.localdate():
            raise ValidationError("Informe uma data de nascimento válida.")
        return data_nascimento

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            self.add_error("confirmar_senha", "As senhas não correspondem.")
        if senha and not self.errors.get("senha"):
            try:
                password_validation.validate_password(senha)
            except ValidationError as error:
                self.add_error("senha", error)
        return cleaned_data


class AgendamentoForm(forms.Form):
    data = forms.DateField(widget=forms.HiddenInput)
    horario = forms.ChoiceField(
        label="Horário disponível",
        choices=[("", "Selecione um horário")],
        widget=forms.RadioSelect,
    )
    profissional = forms.ChoiceField(
        label="Profissional",
        choices=PROFISSIONAL_CHOICES,
    )
    observacao = forms.CharField(
        label="Observação (opcional)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["horario"].widget.attrs["class"] = "slot-input"
        self.fields["profissional"].widget.attrs["class"] = "form-input"
        self.fields["observacao"].widget.attrs["class"] = "form-input"
        if self.is_bound:
            data = self.data.get("data")
            try:
                data = date.fromisoformat(data)
            except (TypeError, ValueError):
                data = None
            profissional = self.data.get("profissional")
            horarios = horarios_para_data(data, profissional) if data else ()
            self.fields["horario"].choices = [
                (horario, horario) for horario in horarios
            ]

    def clean_data(self):
        data = self.cleaned_data["data"]
        if not DATA_INICIO <= data <= DATA_FIM:
            raise ValidationError("Escolha uma data entre 28/11/2026 e 16/12/2026.")
        if data < timezone.localdate():
            raise ValidationError("Não é possível agendar uma data que já passou.")
        return data

    def clean_horario(self):
        horario = self.cleaned_data["horario"]
        if horario not in HORARIOS_VALIDOS:
            raise ValidationError("Selecione um horário disponível.")
        return horario

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        horario = cleaned_data.get("horario")
        profissional = cleaned_data.get("profissional")

        if data and horario and profissional:
            if horario not in horarios_para_data(data, profissional):
                self.add_error("horario", "Esse horário não está disponível nesta data.")
            elif Consulta.objects.filter(
                data=data,
                horario=horario,
                profissional=profissional,
                status=Consulta.STATUS_AGENDADO,
            ).exists():
                self.add_error(
                    "horario",
                    "Esse horário já foi reservado para este profissional. Escolha outro.",
                )
        return cleaned_data

    def dados_profissional(self):
        return PROFISSIONAIS[self.cleaned_data["profissional"]]
