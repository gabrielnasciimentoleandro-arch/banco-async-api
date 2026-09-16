import pytest


async def test_deposito(client, maria, conta_maria):
    r = await client.post(
        "/transacoes/deposito", json={"conta_id": conta_maria["id"], "valor": 99.99}, headers=maria
    )
    assert r.status_code == 201
    assert r.json()["saldo_apos"] == "1099.99"


@pytest.mark.parametrize("valor", [0, -10, 10.123])
async def test_valor_invalido(client, maria, conta_maria, valor):
    r = await client.post(
        "/transacoes/deposito", json={"conta_id": conta_maria["id"], "valor": valor}, headers=maria
    )
    assert r.status_code == 422


async def test_saque(client, maria, conta_maria):
    r = await client.post(
        "/transacoes/saque", json={"conta_id": conta_maria["id"], "valor": 300}, headers=maria
    )
    assert r.status_code == 201
    assert r.json()["saldo_apos"] == "700.00"


async def test_saque_sem_saldo(client, maria):
    conta = (await client.post("/contas", headers=maria)).json()
    r = await client.post("/transacoes/saque", json={"conta_id": conta["id"], "valor": 50}, headers=maria)
    assert r.status_code == 422
    assert "Saldo insuficiente" in r.json()["detail"]


async def test_saque_acima_do_limite_por_operacao(client, maria, conta_maria):
    r = await client.post(
        "/transacoes/saque", json={"conta_id": conta_maria["id"], "valor": 600}, headers=maria
    )
    assert r.status_code == 422
    assert "limite" in r.json()["detail"].lower()


async def test_limite_de_saques_diarios(client, maria, conta_maria):
    corpo = {"conta_id": conta_maria["id"], "valor": 10}
    for _ in range(3):
        assert (await client.post("/transacoes/saque", json=corpo, headers=maria)).status_code == 201
    r = await client.post("/transacoes/saque", json=corpo, headers=maria)
    assert r.status_code == 422
    assert "diários" in r.json()["detail"]


async def test_deposito_em_conta_alheia(client, joao, conta_maria):
    r = await client.post(
        "/transacoes/deposito", json={"conta_id": conta_maria["id"], "valor": 10}, headers=joao
    )
    assert r.status_code == 403


async def test_transferencia(client, maria, joao, conta_maria, conta_joao):
    r = await client.post(
        "/transacoes/transferencia",
        json={
            "conta_origem_id": conta_maria["id"],
            "conta_destino_numero": conta_joao["numero"],
            "valor": 250,
        },
        headers=maria,
    )
    assert r.status_code == 201
    assert r.json()["tipo"] == "transferencia_enviada"
    assert r.json()["saldo_apos"] == "750.00"

    destino = (await client.get(f"/contas/{conta_joao['id']}", headers=joao)).json()
    assert destino["saldo"] == "250.00"
    ext = (await client.get(f"/contas/{conta_joao['id']}/extrato", headers=joao)).json()
    assert ext["transacoes"][0]["tipo"] == "transferencia_recebida"


async def test_transferencia_para_conta_inexistente(client, maria, conta_maria):
    r = await client.post(
        "/transacoes/transferencia",
        json={"conta_origem_id": conta_maria["id"], "conta_destino_numero": "000000-0", "valor": 10},
        headers=maria,
    )
    assert r.status_code == 404


async def test_transferencia_para_si_mesma(client, maria, conta_maria):
    r = await client.post(
        "/transacoes/transferencia",
        json={
            "conta_origem_id": conta_maria["id"],
            "conta_destino_numero": conta_maria["numero"],
            "valor": 10,
        },
        headers=maria,
    )
    assert r.status_code == 422


async def test_saques_concorrentes_nao_deixam_saldo_negativo(client, maria):
    """10 saques simultâneos de 30 em uma conta com 100: no máximo 3 podem passar."""
    import asyncio

    conta = (await client.post("/contas", headers=maria)).json()
    await client.post("/transacoes/deposito", json={"conta_id": conta["id"], "valor": 100}, headers=maria)

    corpo = {"conta_id": conta["id"], "valor": 30}
    respostas = await asyncio.gather(
        *[client.post("/transacoes/saque", json=corpo, headers=maria) for _ in range(10)]
    )
    aprovados = [r for r in respostas if r.status_code == 201]
    assert len(aprovados) == 3

    saldo = (await client.get(f"/contas/{conta['id']}", headers=maria)).json()["saldo"]
    assert saldo == "10.00"
