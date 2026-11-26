# Projeto Barbearia – Django

## Sobre o projeto

Este projeto foi desenvolvido como atividade acadêmica com o objetivo de praticar os conceitos fundamentais do framework Django, utilizando Python no desenvolvimento de aplicações web.

A atividade consiste na criação de uma aplicação com uma tela de login e uma página institucional de uma barbearia, explorando a integração entre templates HTML, rotas e views do Django.

## Tecnologias utilizadas

- **Python** – Linguagem de programação.
- **Django 6.1.3** – Framework para desenvolvimento web.
- **HTML5** – Estruturação das páginas.
- **CSS3** – Estilização das interfaces.
- **Git e GitHub** – Controle de versão e hospedagem do código-fonte.

## Funcionalidades implementadas

- Página inicial com formulário de login.
- Campo para preenchimento de matrícula e senha.
- Redirecionamento para a página institucional da barbearia.
- Renderização de páginas HTML utilizando templates do Django.
- Carregamento de arquivos estáticos utilizando a tag `{% static %}` do Django.
- Organização de rotas e views para navegação entre páginas.

**Observação:** o formulário de login é demonstrativo e ainda não possui autenticação ou validação de usuários.

## Estrutura do projeto

```text
Aula_10.11/
│
├── projeto/
│   ├── templates/
│   │   └── projeto/
│   │       ├── login.html
│   │       └── barbearia.html
│   ├── views.py
│   └── urls.py
│
├── sistema/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── venv/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

- Python 3.13 ou superior.
- pip (gerenciador de pacotes do Python).
- Visual Studio Code (recomendado).

## Como executar o projeto

**1. Clone o repositório:**

```bash
git clone https://github.com/juanvalongo/atividade_django.git
```

**2. Acesse a pasta do projeto:**

```bash
cd Aula_10.11
```

**3. Crie um ambiente virtual:**

```bash
python -m venv venv
```

**4. Ative o ambiente virtual no Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**5. Instale as dependências do projeto:**

```bash
pip install -r requirements.txt
```

**6. Execute o servidor de desenvolvimento:**

```bash
python manage.py runserver
```

**7. Acesse a aplicação pelo navegador:**

```text
http://127.0.0.1:8000/
```

## Dependências

As bibliotecas utilizadas no projeto estão registradas no arquivo `requirements.txt`.

| Dependência | Versão |
|---|---|
| Django | 6.1.3 |
| asgiref | 3.13.0 |
| sqlparse | 0.6.1 |
| tzdata | 2026.6 |

Para instalar todas as dependências, execute:

```bash
pip install -r requirements.txt
```

## Objetivo acadêmico

A atividade tem como finalidade desenvolver conhecimentos práticos sobre o funcionamento do Django, especialmente na organização de projetos, criação de rotas, utilização de views, renderização de templates e integração entre HTML e Python.

O desenvolvimento contribui para a compreensão da arquitetura básica de aplicações web utilizando o framework Django.