# ProntoVital Django

Aplicação web acadêmica em Django que reproduz o fluxo de autenticação e agendamento do frontend mobile ProntoVital. As contas e consultas são persistidas no SQLite configurado pelo Django.

## Requisitos

- Python 3.13 ou superior
- pip

## Executar localmente

No PowerShell, na pasta deste projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Crie uma conta de paciente e entre com e-mail ou CPF. Após entrar, é possível reservar um horário e consultar ou cancelar os próprios agendamentos.

Os horários e profissionais disponíveis entre 28/11/2026 e 16/12/2026 são dados fictícios para demonstração acadêmica.

## Testes

```powershell
python manage.py test
```

## Organização

```text
prontovital_django/
├── projeto/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_cadastrar_options_paciente_consulta.py
│   │   ├── 0003_remove_consulta_unique_active_consulta_slot_and_more.py
│   │   └── 0004_delete_cadastrar.py
│   ├── static/
│   │   ├── css/
│   │   │   └── estilo.css
│   │   └── imagens/
│   │       └── prontovital-logo.png
│   ├── templates/
│   │   └── projeto/
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── cadastro.html
│   │       ├── agendamento.html
│   │       └── visualizar_dados.html
│   ├── admin.py
│   ├── agenda.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── sistema/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

`base.html` reúne a estrutura e os elementos compartilhados pelas páginas. O
ambiente virtual e o banco SQLite local são criados durante a execução e não
fazem parte da estrutura versionada do projeto.
