from datetime import date, timedelta

DATA_INICIO = date(2026, 11, 28)
DATA_FIM = date(2026, 12, 16)

PROFISSIONAIS = {
    "dra-ana-costa": {
        "nome": "Dra. Ana Costa",
        "especialidade": "Clínica Geral",
        "clinica": "Unidade Central (simulação)",
        "horarios_semana": ("08:00", "09:00", "10:00", "13:00", "14:00"),
        "horarios_sabado": ("09:00", "10:00", "11:00"),
    },
    "dr-lucas-almeida": {
        "nome": "Dr. Lucas Almeida",
        "especialidade": "Dermatologia",
        "clinica": "Unidade Boa Vista (simulação)",
        "horarios_semana": ("09:00", "11:00", "14:00", "15:00", "16:00"),
        "horarios_sabado": ("10:00", "11:00", "12:00"),
    },
    "dra-beatriz-lima": {
        "nome": "Dra. Beatriz Lima",
        "especialidade": "Pediatria",
        "clinica": "Unidade Central (simulação)",
        "horarios_semana": ("08:00", "10:00", "11:00", "13:00", "15:00", "16:00"),
        "horarios_sabado": ("09:00", "11:00", "12:00"),
    },
}
HORARIOS_VALIDOS = frozenset(
    horario
    for profissional in PROFISSIONAIS.values()
    for horario in profissional["horarios_semana"] + profissional["horarios_sabado"]
)
PROFISSIONAL_CHOICES = tuple(
    (chave, dados["nome"]) for chave, dados in PROFISSIONAIS.items()
)


def datas_agendamento():
    quantidade_dias = (DATA_FIM - DATA_INICIO).days
    return [DATA_INICIO + timedelta(days=dia) for dia in range(quantidade_dias + 1)]


def horarios_para_data(data, profissional):
    dados_profissional = PROFISSIONAIS.get(profissional)
    if dados_profissional is None:
        return ()
    if data.weekday() == 6:
        return ()
    if data.weekday() == 5:
        return dados_profissional["horarios_sabado"]
    return dados_profissional["horarios_semana"]
