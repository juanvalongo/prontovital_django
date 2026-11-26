from django.contrib import admin
from . models import Cadastrar

class CadastrarAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'senha')
    list_per_page = int = 2
    model = Cadastrar

admin.site.register(Cadastrar, CadastrarAdmin)
