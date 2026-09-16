async def test_registrar_e_logar(client):
    r = await client.post(
        "/auth/registrar", json={"nome": "Ana", "email": "ana@email.com", "senha": "123456"}
    )
    assert r.status_code == 201
    assert "senha" not in r.json() and "senha_hash" not in r.json()

    r = await client.post("/auth/token", data={"username": "ana@email.com", "password": "123456"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


async def test_email_duplicado(client, maria):
    r = await client.post(
        "/auth/registrar", json={"nome": "Xuxa", "email": "maria@email.com", "senha": "123456"}
    )
    assert r.status_code == 409


async def test_senha_errada(client, maria):
    r = await client.post("/auth/token", data={"username": "maria@email.com", "password": "errada"})
    assert r.status_code == 401


async def test_rota_protegida_sem_token(client):
    assert (await client.get("/contas")).status_code == 401


async def test_token_invalido(client):
    r = await client.get("/contas", headers={"Authorization": "Bearer token.falso.aqui"})
    assert r.status_code == 401


async def test_eu(client, maria):
    r = await client.get("/auth/eu", headers=maria)
    assert r.status_code == 200
    assert r.json()["email"] == "maria@email.com"


async def test_login_email_nao_diferencia_maiusculas(client, maria):
    r = await client.post("/auth/token", data={"username": "MARIA@Email.com", "password": "segredo1"})
    assert r.status_code == 200
