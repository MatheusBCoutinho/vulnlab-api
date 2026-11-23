# 🧪 VulnLab API | BOLA / IDOR Security Laboratory

**Português** | [English](#english)

> ⚠️ **Aplicação intencionalmente vulnerável.** Execute apenas em `127.0.0.1`, em ambiente próprio ou autorizado. Não faça deploy público.

## Português

### Objetivo
API didática que compara uma falha de autorização em nível de objeto (**BOLA/IDOR**) com uma implementação que valida o proprietário do recurso. A API possui autenticação simples por **token opaco em memória**, não JWT.

### Tecnologias
Python 3.10+, FastAPI, SQLite em memória, Uvicorn, pytest, HTTPX e GitHub Actions.

### Executar no Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Caso a política do PowerShell bloqueie a ativação, use diretamente `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` e `.\.venv\Scripts\python.exe -m pytest -q` (e o mesmo Python para `-m uvicorn`).

Abra <http://127.0.0.1:8000/docs>. O endpoint `POST /login` recebe `username` e `password` como **query parameters** nesta versão didática; não use esse padrão para credenciais reais.

Contas **fictícias**: `alice / alice123` (fatura 1) e `bob / bob123` (fatura 2). Faça login, copie `access_token`, clique em **Authorize** e informe o token conforme a interface Bearer. Autenticado como Alice, compare:

| Requisição | Resultado esperado |
|---|---|
| `GET /lab/invoices/2` | **200**: erro intencional de autorização |
| `GET /secure/invoices/2` | **403**: acesso negado |
| `GET /secure/invoices/1` | **200**: acesso autorizado |

### Estrutura

```text
app/main.py                 API, dados fictícios, autenticação e rotas
app/__init__.py             Pacote Python
tests/test_api.py           3 testes automatizados
.github/workflows/ci.yml   Testes em push e pull request
requirements.txt           Dependências
.gitignore                 Arquivos locais não versionados
README.md                  Documentação bilíngue
```

### O que a falha demonstra
Autenticar não é autorizar. A rota vulnerável permite que um usuário autenticado consulte uma fatura de outra pessoa ao alterar o identificador. A rota corrigida exige `invoice['owner_id'] == current_user`.

### Limitações
Laboratório simplificado: usuários e tokens apenas em memória; tokens expiram ao reiniciar o processo; senhas didáticas com SHA-256 simples (inadequado para aplicações reais); sem controle de concorrência do SQLite compartilhado; sem rate limiting ou logs de auditoria. **Não é uma API pronta para produção.** Não enviar credenciais reais: neste MVP o login usa parâmetros de consulta, que podem aparecer em logs e históricos.

### Referências
- [OWASP API Security](https://owasp.org/API-Security/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## English

> ⚠️ **Intentionally vulnerable training API.** Run locally on `127.0.0.1` only. Never deploy publicly.

### Purpose
Demonstrate **Broken Object Level Authorization (BOLA/IDOR)** through an intentionally flawed invoice endpoint and a corrected endpoint that enforces resource ownership.

### Tech stack
Python 3.10+, FastAPI, in-memory SQLite, Uvicorn, pytest, HTTPX, and GitHub Actions. Authentication uses **in-memory opaque bearer tokens**, not JWT.

### Install and run

```bash
python -m venv .venv
# Activate the virtual environment for your OS
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/docs>. Use the demo account `alice / alice123` with `POST /login` (query parameters for this training MVP), then authorize with the issued bearer token. Compare `GET /lab/invoices/2` (**200**, intentional flaw) and `GET /secure/invoices/2` (**403**, access denied). Alice may retrieve her own invoice via `GET /secure/invoices/1` (**200**).

### Security model and limitations
The vulnerable route authenticates the caller but omits ownership checks. The fixed route enforces `owner_id`. All users and invoices are fictional; state is in memory. Demo password hashing is **not suitable for production**, and login query parameters can expose submitted values in logs. No public deployment, real data, or real credentials.

### Tests
Run `python -m pytest -q`. CI runs the same tests on GitHub Actions.
