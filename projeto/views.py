from django.shortcuts import render
from . models import Cadastrar

def pagina_login(request):
    return render(request, 'projeto/login.html')

def pagina_barbearia(request):
    return render(request, 'projeto/barbearia.html')

def mostrar_dados(request):
    mostrar = Cadastrar.objects.all()
    return render(request, 'projeto/visualizar_matricula.html', {'mostrar': mostrar})
