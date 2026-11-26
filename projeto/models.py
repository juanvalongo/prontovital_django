from django.db import models

class Cadastrar(models.Model):
    matricula = models.IntegerField()
    senha = models.CharField(max_length= 255)    

    class Meta:
        verbose_name = "Cadastro"
        verbose_name_plural = "Cadastros"

    def __str__(self):
        return str(self.matricula)       
