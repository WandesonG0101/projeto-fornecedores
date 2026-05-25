# Cadastro de Fornecedores

Sistema web em Django para cadastro, validacao documental e integracao futura de fornecedores com setores como compras, financeiro, contratos, almoxarifado, fiscalizacao e gestao administrativa.

## Arquitetura

- `core`: base compartilhada, paginacao, renderer JSON, permissoes, validadores e health check.
- `accounts`: configuracoes iniciais de usuarios, grupos e comando de bootstrap.
- `suppliers`: fornecedores, categorias, contatos e dados bancarios.
- `documents`: documentos vinculados aos fornecedores.
- `integrations`: logs e cliente base para comunicacao com APIs externas/internas.
- `config`: settings, urls globais e rotas versionadas.

## Decisoes tecnicas

- API REST versionada em `/api/v1/`.
- Swagger/OpenAPI em `/api/docs/` e schema em `/api/schema/`.
- Respostas JSON padronizadas pelo renderer `core.renderers.StandardJSONRenderer`.
- SQLite por padrao em desenvolvimento e PostgreSQL via `DATABASE_URL`.
- Permissoes por grupos: `Administrador`, `Cadastrador`, `Analista` e `Somente leitura`.
- Dados bancarios e observacoes internas nao sao expostos para perfil somente leitura.
- Upload de documentos limitado por extensao e tamanho configuravel.
- Health check publico em `/health/` para monitoramento.
- Logs de integracao disponiveis para administradores em `/api/v1/integracoes/logs/`.

## Instalacao no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py bootstrap_system
python manage.py createsuperuser
python manage.py runserver
```

Se o PowerShell bloquear a ativacao do ambiente virtual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Variaveis de ambiente

Copie `.env.example` para `.env`. Por padrao, o projeto usa SQLite. Para PostgreSQL:

```env
DATABASE_URL=postgresql://fornecedores:fornecedores@localhost:5432/fornecedores
```

Toggles de seguranca para producao:

```env
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## Endpoints principais

- `GET /health/`
- `GET/POST /api/v1/fornecedores/`
- `GET/PATCH/PUT /api/v1/fornecedores/{id}/`
- `POST /api/v1/fornecedores/{id}/inativar/`
- `GET /api/v1/fornecedores/por-categoria/{categoria_id}/`
- `GET/POST /api/v1/fornecedores/{id}/documentos/`
- `GET/POST /api/v1/categorias/`
- `GET/POST /api/v1/contatos/`
- `GET/POST /api/v1/dados-bancarios/`
- `GET/POST /api/v1/documentos/`
- `PATCH /api/v1/documentos/{id}/`
- `GET /api/v1/integracoes/logs/`

## Testes e validacao

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Observacoes para evolucao

- JWT pode ser adicionado depois sem trocar os ViewSets atuais.
- Dados bancarios ja estao separados para permitir auditoria, mascaramento e permissoes mais finas.
- A camada `integrations/services/api_client.py` centraliza chamadas externas e grava `IntegrationLog`.
- O admin foi configurado para operacao interna, mas os fluxos de integracao devem priorizar a API versionada.
