# Sistema de Cadastro de Fornecedores

Projeto academico em Django para cadastro, listagem, busca, edicao e exclusao de fornecedores.

## Tecnologias

- Python
- Django
- SQLite
- HTML
- Bootstrap 5

## Como rodar

Instale as dependencias:

```powershell
python -m pip install -r requirements.txt
```

Crie as tabelas do banco:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Crie um usuario para login:

```powershell
python manage.py createsuperuser
```

Inicie o servidor:

```powershell
python manage.py runserver
```

Depois acesse:

```text
http://127.0.0.1:8000/login/
```

Tambem e possivel iniciar no Windows com dois cliques no arquivo:

```text
iniciar_servidor.bat
```
