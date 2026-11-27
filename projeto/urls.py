from django.urls import path
from . import views

urlpatterns = [
    path("", views.pagina_login, name="login"),
    path("cadastro/", views.cadastrar_paciente, name="cadastro"),
    path("sair/", views.sair, name="logout"),
    path("agendamento/", views.pagina_agendamento, name="agendamento"),
    path("visualizar-dados/", views.mostrar_dados, name="visualizar_dados"),
    path(
        "consultas/<int:consulta_id>/cancelar/",
        views.cancelar_consulta,
        name="cancelar_consulta",
    ),
]