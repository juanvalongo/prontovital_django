from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Consulta, Paciente

User = get_user_model()


class FluxoPacienteTests(TestCase):
    def dados_cadastro(self, **overrides):
        dados = {
            "nome": "Joana da Silva",
            "email": "joana@example.com",
            "senha": "SaudeSegura2026!xyz",
            "confirmar_senha": "SaudeSegura2026!xyz",
            "telefone": "(81) 99999-1234",
            "cpf": "123.456.789-01",
            "endereco": "Rua das Flores, 10",
            "cidade": "Recife",
            "estado": "PE",
            "data_nascimento": "1990-05-10",
            "sexo": "Feminino",
            "observacoes": "Alergia demonstrativa",
        }
        dados.update(overrides)
        return dados

    def criar_paciente(self, email, cpf):
        usuario = User.objects.create_user(
            username=email,
            email=email,
            password="SaudeSegura2026!xyz",
            first_name=email.split("@")[0],
        )
        paciente = Paciente.objects.create(
            usuario=usuario,
            cpf=cpf,
            telefone="81999991234",
            endereco="Rua das Flores, 10",
            cidade="Recife",
            estado="PE",
            data_nascimento=date(1990, 5, 10),
            sexo="Outro",
        )
        return usuario, paciente

    def test_cadastro_usa_hash_de_senha_e_login_pode_usar_cpf(self):
        response = self.client.post(reverse("cadastro"), self.dados_cadastro())

        self.assertRedirects(response, reverse("login"))
        usuario = User.objects.get(email="joana@example.com")
        self.assertTrue(usuario.check_password("SaudeSegura2026!xyz"))
        self.assertNotEqual(usuario.password, "SaudeSegura2026!xyz")

        response = self.client.post(
            reverse("login"),
            {"identificador": "123.456.789-01", "senha": "SaudeSegura2026!xyz"},
        )
        self.assertRedirects(response, reverse("agendamento"))

    def test_agendamento_e_salvo_e_exibido_somente_para_o_paciente(self):
        usuario, paciente = self.criar_paciente("joana@example.com", "12345678901")
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("agendamento"),
            {
                "data": "2026-11-30",
                "horario": "09:00",
                "profissional": "dra-ana-costa",
                "observacao": "Consulta de demonstração",
            },
        )

        self.assertRedirects(response, reverse("visualizar_dados"))
        consulta = Consulta.objects.get(paciente=paciente)
        self.assertEqual(consulta.data, date(2026, 11, 30))
        self.assertEqual(consulta.horario, time(9, 0))

        response = self.client.get(reverse("visualizar_dados"))
        self.assertContains(response, "Consulta de demonstração")

        outro_usuario, _ = self.criar_paciente("outro@example.com", "98765432100")
        self.client.force_login(outro_usuario)
        response = self.client.get(reverse("visualizar_dados"))
        self.assertNotContains(response, "Consulta de demonstração")

    def test_nao_permite_reservar_horario_ocupado(self):
        usuario, paciente = self.criar_paciente("joana@example.com", "12345678901")
        _, outro_paciente = self.criar_paciente("outra@example.com", "98765432100")
        Consulta.objects.create(
            paciente=outro_paciente,
            data=date(2026, 11, 30),
            horario=time(9, 0),
            profissional="dra-ana-costa",
            especialidade="Clínica Geral",
            clinica="Unidade Central (simulação)",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("agendamento"),
            {
                "data": "2026-11-30",
                "horario": "09:00",
                "profissional": "dra-ana-costa",
                "observacao": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Consulta.objects.count(), 1)
        self.assertContains(response, "reservado")

    def test_disponibilidade_considera_o_profissional_selecionado(self):
        usuario, _ = self.criar_paciente("joana@example.com", "12345678901")
        _, outro_paciente = self.criar_paciente("outro@example.com", "98765432100")
        Consulta.objects.create(
            paciente=outro_paciente,
            data=date(2026, 11, 30),
            horario=time(9, 0),
            profissional="dra-ana-costa",
            especialidade="Clínica Geral",
            clinica="Unidade Central (simulação)",
        )
        self.client.force_login(usuario)

        response = self.client.get(
            reverse("agendamento"),
            {"data": "2026-11-30", "profissional": "dra-ana-costa"},
        )
        self.assertContains(response, 'onchange="this.form.submit()"')
        self.assertNotContains(response, "Ver horários")
        self.assertNotContains(response, 'id="id_profissional"')
        self.assertNotContains(response, 'value="09:00"')

        response = self.client.get(
            reverse("agendamento"),
            {"data": "2026-11-30", "profissional": "dr-lucas-almeida"},
        )
        self.assertContains(response, 'value="09:00"')
        self.assertContains(response, 'value="16:00"')
        self.assertNotContains(response, 'value="08:00"')

    def test_agendamento_requer_login(self):
        response = self.client.get(reverse("agendamento"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('agendamento')}")

    def test_telas_de_login_cadastro_agendamento_e_historico_renderizam(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cadastro")).status_code, 200)

        usuario, _ = self.criar_paciente("joana@example.com", "12345678901")
        self.client.force_login(usuario)
        self.assertEqual(self.client.get(reverse("agendamento")).status_code, 200)
        self.assertEqual(self.client.get(reverse("visualizar_dados")).status_code, 200)

    def test_cancelamento_so_atinge_consulta_do_paciente_autenticado(self):
        usuario, _ = self.criar_paciente("joana@example.com", "12345678901")
        _, outro_paciente = self.criar_paciente("outro@example.com", "98765432100")
        consulta = Consulta.objects.create(
            paciente=outro_paciente,
            data=date(2026, 11, 30),
            horario=time(9, 0),
            profissional="dra-ana-costa",
            especialidade="Clínica Geral",
            clinica="Unidade Central (simulação)",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("cancelar_consulta", args=[consulta.pk]),
        )

        self.assertEqual(response.status_code, 404)
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, Consulta.STATUS_AGENDADO)

    def test_paciente_pode_cancelar_e_liberar_o_horario(self):
        usuario, paciente = self.criar_paciente("joana@example.com", "12345678901")
        consulta = Consulta.objects.create(
            paciente=paciente,
            data=date(2026, 11, 30),
            horario=time(9, 0),
            profissional="dra-ana-costa",
            especialidade="Clínica Geral",
            clinica="Unidade Central (simulação)",
        )
        self.client.force_login(usuario)

        response = self.client.post(
            reverse("cancelar_consulta", args=[consulta.pk]),
        )

        self.assertRedirects(response, reverse("visualizar_dados"))
        consulta.refresh_from_db()
        self.assertEqual(consulta.status, Consulta.STATUS_CANCELADO)
        self.assertEqual(Consulta.objects.filter(data=date(2026, 11, 30), status="agendado").count(), 0)
