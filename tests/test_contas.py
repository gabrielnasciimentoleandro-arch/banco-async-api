async def test_abrir_conta(client, maria):
    r = await client.post("/contas", headers=maria)
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["saldo"] == "0.00"
    assert len(corpo["numero"]) == 8


async def test_listar_somente_minhas_contas(client, maria, joao, conta_maria):
    assert len((await client.get("/contas", headers=maria)).json()) == 1
    assert (await client.get("/contas", headers=joao)).json() == []


async def test_consultar_conta_de_outro_cliente(client, joao, conta_maria):
    r = await client.get(f"/contas/{conta_maria['id']}", headers=joao)
    assert r.status_code == 403


async def test_conta_inexistente(client, maria):
    assert (await client.get("/contas/999", headers=maria)).status_code == 404


async def test_extrato(client, maria, conta_maria):
    cid = conta_maria["id"]
    await client.post(
        "/transacoes/saque", json={"conta_id": cid, "valor": 200, "descricao": "Mercado"}, headers=maria
    )
    r = await client.get(f"/contas/{cid}/extrato", headers=maria)
    assert r.status_code == 200
    ext = r.json()
    assert ext["conta"]["saldo"] == "800.00"
    assert ext["total_depositos"] == "1000.00"
    assert ext["total_saques"] == "200.00"
    assert len(ext["transacoes"]) == 2
    assert ext["transacoes"][0]["tipo"] == "saque"
    assert ext["transacoes"][0]["descricao"] == "Mercado"
