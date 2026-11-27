import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST, require_http_methods

from .agenda import (
    DATA_FIM,
    DATA_INICIO,
    PROFISSIONAIS,
    datas_agendamento,
    horarios_para_data,
)
from .forms import AgendamentoForm, CadastroPacienteForm
from .models import Consulta, Paciente

User = get_user_model()


@require_http_methods(["GET", "POST"])
def pagina_login(request):
    if request.user.is_authenticated:
        return redirect("agendamento")

    if request.method == "POST":
        identificador = request.POST.get("identificador", "").strip()
        senha = request.POST.get("senha", "")
        nome_usuario = identificador.lower()

        if "@" not in identificador:
            cpf = re.sub(r"\D", "", identificador)
            paciente = Paciente.objects.select_related("usuario").filter(cpf=cpf).first()
            if paciente:
                nome_usuario = paciente.usuario.username

        usuario = authenticate(
            request,
            username=nome_usuario,
            password=senha,
        )
        if usuario is not None:
            login(request, usuario)
            return redirect("agendamento")

        messages.error(request, "E-mail/CPF ou senha incorretos.")

    return render(request, "projeto/login.html")


@require_http_methods(["GET", "POST"])
def cadastrar_paciente(request):
    if request.user.is_authenticated:
        return redirect("agendamento")

    form = CadastroPacienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data
        nomes = dados["nome"].strip().split()
        try:
            with transaction.atomic():
                usuario = User.objects.create_user(
                    username=dados["email"],
                    email=dados["email"],
                    first_name=nomes[0],
                    last_name=" ".join(nomes[1:]),
                    password=dados["senha"],
                )
                Paciente.objects.create(
                    usuario=usuario,
                    cpf=dados["cpf"],
                    telefone=dados["telefone"],
                    endereco=dados["endereco"].strip(),
                    cidade=dados["cidade"].strip(),
                    estado=dados["estado"].upper(),
                    data_nascimento=dados["data_nascimento"],
                    sexo=dados["sexo"],
                    observacoes=dados["observacoes"].strip(),
                )
        except IntegrityError:
            form.add_error(None, "Não foi possível concluir o cadastro. Confira o e-mail e o CPF.")
        else:
            messages.success(request, "Conta criada com sucesso. Entre com seu e-mail ou CPF.")
            return redirect("login")

    return render(request, "projeto/cadastro.html", {"form": form})


@require_POST
def sair(request):
    logout(request)
    messages.success(request, "Você saiu da sua conta.")
    return redirect("login")


@login_required
@require_http_methods(["GET", "POST"])
def pagina_agendamento(request):
    data_solicitada = request.POST.get("data") if request.method == "POST" else request.GET.get("data")
    data_selecionada = parse_date(data_solicitada) if data_solicitada else DATA_INICIO
    profissional_solicitado = (
        request.POST.get("profissional")
        if request.method == "POST"
        else request.GET.get("profissional")
    )
    if profissional_solicitado not in PROFISSIONAIS:
        profissional_solicitado = next(iter(PROFISSIONAIS))

    if data_selecionada is None or not DATA_INICIO <= data_selecionada <= DATA_FIM:
        messages.error(request, "Escolha uma data entre 28/11/2026 e 16/12/2026.")
        data_selecionada = DATA_INICIO

    form = AgendamentoForm(
        request.POST or None,
        initial={
            "data": data_selecionada,
            "profissional": profissional_solicitado,
        },
    )
    if request.method == "POST" and form.is_valid():
        perfil = get_object_or_404(Paciente, usuario=request.user)
        profissional = form.dados_profissional()
        try:
            with transaction.atomic():
                Consulta.objects.create(
                    paciente=perfil,
                    data=form.cleaned_data["data"],
                    horario=datetime.strptime(form.cleaned_data["horario"], "%H:%M").time(),
                    profissional=form.cleaned_data["profissional"],
                    especialidade=profissional["especialidade"],
                    clinica=profissional["clinica"],
                    observacao=form.cleaned_data["observacao"].strip(),
                )
        except IntegrityError:
            form.add_error("horario", "Esse horário acabou de ser reservado. Escolha outro.")
        else:
            messages.success(request, "Consulta agendada. Os dados foram salvos no banco.")
            return redirect("visualizar_dados")

    horarios = horarios_para_data(data_selecionada, profissional_solicitado)
    reservados = set(
        Consulta.objects.filter(
            data=data_selecionada,
            profissional=profissional_solicitado,
            status=Consulta.STATUS_AGENDADO,
        ).values_list("horario", flat=True)
    )
    horarios_disponiveis = [
        horario
        for horario in horarios
        if datetime.strptime(horario, "%H:%M").time() not in reservados
    ]

    return render(
        request,
        "projeto/agendamento.html",
        {
            "form": form,
            "datas": datas_agendamento(),
            "data_selecionada": data_selecionada,
            "horarios_disponiveis": horarios_disponiveis,
            "profissionais": PROFISSIONAIS,
            "profissional_selecionado": profissional_solicitado,
        },
    )


@login_required
def mostrar_dados(request):
    consultas = Consulta.objects.filter(
        paciente__usuario=request.user,
    ).select_related("paciente")
    return render(
        request,
        "projeto/visualizar_dados.html",
        {
            "consultas": consultas,
            "consultas_ativas": consultas.filter(status=Consulta.STATUS_AGENDADO).count(),
        },
    )


@login_required
@require_POST
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(
        Consulta,
        pk=consulta_id,
        paciente__usuario=request.user,
        status=Consulta.STATUS_AGENDADO,
    )
    consulta.status = Consulta.STATUS_CANCELADO
    consulta.save(update_fields=["status"])
    messages.success(request, "Consulta cancelada. O horário voltou a ficar disponível.")
    return redirect("visualizar_dados")
