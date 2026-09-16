import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./teste.db"
os.environ["LIMITE_SAQUE_VALOR"] = "500"
os.environ["LIMITE_SAQUES_DIARIOS"] = "3"

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
async def banco_limpo():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def _autenticar(client, email, senha="segredo1", nome="Cliente Teste"):
    await client.post("/auth/registrar", json={"nome": nome, "email": email, "senha": senha})
    r = await client.post("/auth/token", data={"username": email, "password": senha})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
async def maria(client):
    return await _autenticar(client, "maria@email.com", nome="Maria")


@pytest.fixture
async def joao(client):
    return await _autenticar(client, "joao@email.com", nome="João")


@pytest.fixture
async def conta_maria(client, maria):
    r = await client.post("/contas", headers=maria)
    conta = r.json()
    await client.post("/transacoes/deposito", json={"conta_id": conta["id"], "valor": 1000}, headers=maria)
    return conta


@pytest.fixture
async def conta_joao(client, joao):
    return (await client.post("/contas", headers=joao)).json()
