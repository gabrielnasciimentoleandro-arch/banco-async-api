# 🏦 Banco Async API

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1xx-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)
![Tests](https://img.shields.io/badge/tests-25%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

API bancária **assíncrona** desenvolvida com **FastAPI** e **SQLAlchemy 2.0** como solução autoral do desafio *"Criando sua API Bancária Assíncrona com FastAPI"* do bootcamp de Python da [DIO](https://www.dio.me/).

Permite cadastrar clientes, abrir contas correntes, realizar **depósitos, saques e transferências**, e consultar o **extrato** — tudo protegido por autenticação **JWT** e documentado automaticamente via **OpenAPI/Swagger**.

---

## 📌 Sumário

- [Funcionalidades](#-funcionalidades)
- [Regras de negócio](#-regras-de-negócio)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Modelagem de dados](#-modelagem-de-dados)
- [Como executar](#-como-executar)
- [Como usar](#-como-usar)
- [Testes](#-testes)
- [Decisões de projeto](#-decisões-de-projeto)

---

## ✨ Funcionalidades

| Método | Rota | Descrição | Auth |
|:--|:--|:--|:--:|
| `POST` | `/auth/registrar` | Cadastra um cliente (senha com hash Argon2) | – |
| `POST` | `/auth/token` | Login (OAuth2 password flow) → token JWT | – |
| `GET`  | `/auth/eu` | Dados do cliente autenticado | 🔒 |
| `POST` | `/contas` | Abre uma conta corrente (número gerado automaticamente) | 🔒 |
| `GET`  | `/contas` | Lista as contas do cliente | 🔒 |
| `GET`  | `/contas/{id}` | Consulta saldo de uma conta | 🔒 |
| `GET`  | `/contas/{id}/extrato` | **Extrato**: saldo, totais e histórico de transações | 🔒 |
| `POST` | `/transacoes/deposito` | Realiza depósito | 🔒 |
| `POST` | `/transacoes/saque` | Realiza saque | 🔒 |
| `POST` | `/transacoes/transferencia` | Transfere para outra conta pelo número | 🔒 |

## 📏 Regras de negócio

| Regra | Resposta |
|:--|:--|
| Valor deve ser **positivo** e ter no máximo 2 casas decimais | `422` |
| Saque/transferência exige **saldo suficiente** | `422` com saldo atual |
| Saque/transferência limitados a **R$ 500,00 por operação** (configurável) | `422` |
| Máximo de **3 saques/transferências por dia** (configurável) | `422` |
| Cliente só acessa/movimenta **as próprias contas** | `403` |
| E-mail único por cliente | `409` |
| Transferência é **atômica**: débito e crédito na mesma transação de banco | – |
| Cada transação grava o **saldo após a operação** (auditoria) | – |

---

## 🛠 Tecnologias

| Camada | Ferramenta |
|:--|:--|
| Framework web | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM assíncrono | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) (`AsyncSession`, `Mapped`) + aiosqlite |
| Validação / config | Pydantic v2 + pydantic-settings |
| Autenticação | JWT ([PyJWT](https://pyjwt.readthedocs.io/)) + OAuth2 Password Bearer |
| Hash de senha | [pwdlib](https://github.com/frankie567/pwdlib) (Argon2id) |
| Testes | pytest + pytest-asyncio + httpx |
| Servidor | Uvicorn |

---

## 🧱 Arquitetura

Organização **por domínio** (feature-based): cada pasta reúne modelo, schemas, regras e rotas de um mesmo contexto.

```
banco-async-api/
├── app/
│   ├── main.py                 # instância FastAPI, lifespan e routers
│   ├── core/
│   │   ├── config.py           # settings via .env
│   │   ├── database.py         # engine async, sessão e Base declarativa
│   │   ├── seguranca.py        # hash de senha, JWT e dependência ClienteAtual
│   │   └── excecoes.py         # exceções HTTP de domínio
│   ├── clientes/               # cadastro e login
│   │   ├── models.py  ├── schemas.py  └── router.py
│   ├── contas/                 # abertura, consulta e extrato
│   │   ├── models.py  ├── schemas.py  ├── service.py  └── router.py
│   └── transacoes/             # depósito, saque e transferência
│       ├── models.py  ├── schemas.py  ├── service.py  └── router.py
├── tests/                      # 25 testes de integração
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

Fluxo de uma requisição: **router** (HTTP, validação Pydantic) → **service** (regras de negócio) → **models** (persistência via `AsyncSession`).

---

## 🗄 Modelagem de dados

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────────┐
│   clientes   │       │      contas      │       │      transacoes      │
├──────────────┤       ├──────────────────┤       ├──────────────────────┤
│ id        PK │──┐    │ id            PK │──┐    │ id                PK │
│ nome         │  └──< │ cliente_id    FK │  └──< │ conta_id          FK │
│ email  UNIQUE│       │ numero    UNIQUE │       │ tipo            enum │
│ senha_hash   │       │ agencia          │       │ valor                │
│ criado_em    │       │ saldo            │       │ saldo_apos           │
└──────────────┘       │ criada_em        │       │ descricao            │
                       └──────────────────┘       │ realizada_em         │
   1 cliente ── N contas ── N transações          └──────────────────────┘
```

`tipo` ∈ `deposito` · `saque` · `transferencia_enviada` · `transferencia_recebida`

---

## 🚀 Como executar

```bash
git clone https://github.com/gabrielnasciimentoleandro-arch/banco-async-api.git
cd banco-async-api

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env               # ajuste SECRET_KEY e limites se quiser

uvicorn app.main:app --reload
```

As tabelas são criadas automaticamente na inicialização. Documentação interativa:

- Swagger UI → http://localhost:8000/docs (assets servidos localmente, com **tema escuro** — funciona offline)
- ReDoc → http://localhost:8000/redoc

### Variáveis de ambiente

| Variável | Padrão | Descrição |
|:--|:--|:--|
| `DATABASE_URL` | `sqlite+aiosqlite:///./banco.db` | URL async do banco (aceita PostgreSQL com `asyncpg`) |
| `SECRET_KEY` | – | Chave de assinatura do JWT (`openssl rand -hex 32`) |
| `TOKEN_EXPIRA_MINUTOS` | `60` | Validade do token |
| `LIMITE_SAQUE_VALOR` | `500.00` | Valor máximo por saque/transferência |
| `LIMITE_SAQUES_DIARIOS` | `3` | Quantidade de saques/transferências por dia |

---

## 🧭 Como usar

No Swagger (`/docs`):

1. **POST /auth/registrar** → `{"nome": "Maria Silva", "email": "maria@email.com", "senha": "senha123"}`
2. Clique em **Authorize 🔓**, informe e-mail e senha — o Swagger obtém o token sozinho.
3. **POST /contas** → cria a conta e devolve o número (ex.: `898343-5`).
4. **POST /transacoes/deposito** → `{"conta_id": 1, "valor": 1000, "descricao": "Salário"}`
5. **POST /transacoes/saque** → `{"conta_id": 1, "valor": 150, "descricao": "Mercado"}`
6. **GET /contas/1/extrato**:

```json
{
  "conta": { "id": 1, "numero": "898343-5", "agencia": "0001", "saldo": "850.00", "criada_em": "..." },
  "total_depositos": "1000.00",
  "total_saques": "150.00",
  "transacoes": [
    { "id": 2, "tipo": "saque",    "valor": "150.00",  "saldo_apos": "850.00",  "descricao": "Mercado", "realizada_em": "..." },
    { "id": 1, "tipo": "deposito", "valor": "1000.00", "saldo_apos": "1000.00", "descricao": "Salário", "realizada_em": "..." }
  ]
}
```

Via terminal:

```bash
TOKEN=$(curl -s -X POST localhost:8000/auth/token \
  -d 'username=maria@email.com&password=senha123' | jq -r .access_token)

curl -X POST localhost:8000/transacoes/saque \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"conta_id": 1, "valor": 700}'
# → 422 {"detail": "O valor excede o limite de R$ 500.00 por operação."}
```

---

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

25 testes de integração cobrindo: cadastro/login, e-mail duplicado, senha incorreta, token ausente/inválido, abertura e isolamento de contas entre clientes, depósito, valores inválidos (zero, negativo, 3 casas decimais), saque, saldo insuficiente, limite por operação, limite diário, transferência (sucesso, destino inexistente, mesma conta), extrato e **saques concorrentes** (10 requisições simultâneas não podem deixar saldo negativo).

---

## 💡 Decisões de projeto

- **SQLAlchemy 2.0 ORM async** em vez de query builder: modelos tipados com `Mapped[...]`, relacionamentos e sessão gerenciada por dependência do FastAPI.
- **Login real** com e-mail e senha (Argon2) e `OAuth2PasswordBearer`, o que integra nativamente com o botão *Authorize* do Swagger.
- **Identidade vem do token**: o `cliente_id` nunca é enviado no corpo da requisição — evita que um cliente movimente a conta de outro.
- **`Decimal`** para valores monetários, evitando erros de arredondamento de `float`.
- **`saldo_apos`** em cada transação: extrato auditável sem recalcular histórico.
- **Débito atômico no banco** (`UPDATE ... WHERE saldo >= valor`): protege contra condição de corrida quando várias requisições sacam da mesma conta ao mesmo tempo — ler o saldo em Python e depois gravar permitiria saldo negativo.
- **Erros de regra de negócio como `422`**, distinguindo de `404` (não existe) e `403` (não é seu).
- Estrutura **por domínio**, que escala melhor do que separar por tipo de arquivo (`models/`, `schemas/`...) conforme o projeto cresce.

### Próximos passos
- [ ] Migrações com Alembic
- [ ] Docker + PostgreSQL
- [ ] Paginação no extrato e filtro por período
- [ ] Refresh token

---

## 👤 Autor

**Gabriel Nascimento Leandro**
[![GitHub](https://img.shields.io/badge/GitHub-gabrielnasciimentoleandro--arch-181717?logo=github)](https://github.com/gabrielnasciimentoleandro-arch)

Projeto desenvolvido para o desafio *"Criando sua API Bancária Assíncrona com FastAPI"* — Bootcamp Python, [DIO](https://www.dio.me/).

## 📄 Licença

MIT
