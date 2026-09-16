from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.clientes.router import router as auth_router
from app.contas.router import router as contas_router
from app.core.database import criar_tabelas
from app.transacoes.router import router as transacoes_router

DESCRICAO = """
API bancária **assíncrona** construída com FastAPI e SQLAlchemy 2.0 para o desafio da DIO. 🏦

### Como usar
1. Cadastre-se em **POST /auth/registrar**.
2. Clique em **Authorize**, informe e-mail e senha (o token JWT é obtido automaticamente).
3. Abra uma conta em **POST /contas**.
4. Movimente com **/transacoes/deposito**, **/transacoes/saque** e **/transacoes/transferencia**.
5. Veja o **extrato** em **GET /contas/{id}/extrato**.

### Regras
* Valores devem ser positivos, com até 2 casas decimais.
* Saques e transferências exigem saldo, respeitam um limite por operação e um limite diário de operações.
* Cada cliente só enxerga e movimenta as próprias contas.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await criar_tabelas()
    yield


app = FastAPI(
    title="Banco Async API",
    version="1.0.0",
    summary="Depósitos, saques, transferências e extrato com autenticação JWT.",
    description=DESCRICAO,
    lifespan=lifespan,
    docs_url=None,  # Swagger servido localmente em /docs (sem depender de CDN)
    contact={
        "name": "Gabriel Nascimento Leandro",
        "url": "https://github.com/gabrielnasciimentoleandro-arch",
    },
    license_info={"name": "MIT"},
)

# Swagger UI com assets locais: funciona mesmo sem acesso a CDN externo
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/docs", include_in_schema=False)
async def swagger_ui() -> HTMLResponse:
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    ).body.decode()
    # Injeta o tema escuro logo após o CSS padrão do Swagger
    html = html.replace("</head>", '<link rel="stylesheet" href="/static/tema-escuro.css"></head>')
    return HTMLResponse(html)


app.include_router(auth_router)
app.include_router(contas_router)
app.include_router(transacoes_router)


@app.get("/", include_in_schema=False)
async def raiz():
    return RedirectResponse(url="/docs")
