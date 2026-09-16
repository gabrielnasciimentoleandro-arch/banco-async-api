from typing import Any

from fastapi import APIRouter, status

from app.core.database import Sessao
from app.core.seguranca import ClienteAtual
from app.transacoes import service
from app.transacoes.schemas import Movimentacao, TransacaoPublica, Transferencia

router = APIRouter(prefix="/transacoes", tags=["Transações"])

_respostas: dict[int | str, dict[str, Any]] = {
    403: {"description": "Conta de outro cliente"},
    404: {"description": "Conta não encontrada"},
    422: {"description": "Dados inválidos ou regra de negócio violada (saldo, limite)"},
}


@router.post(
    "/deposito",
    status_code=status.HTTP_201_CREATED,
    response_model=TransacaoPublica,
    summary="Realizar depósito",
    description="Credita o valor informado na conta. Apenas valores **positivos** são aceitos.",
    responses=_respostas,
)
async def depositar(dados: Movimentacao, cliente: ClienteAtual, session: Sessao):
    return await service.depositar(session, cliente.id, dados.conta_id, dados.valor, dados.descricao)


@router.post(
    "/saque",
    status_code=status.HTTP_201_CREATED,
    response_model=TransacaoPublica,
    summary="Realizar saque",
    description=(
        "Debita o valor da conta. Regras: valor positivo, **saldo suficiente**, "
        "valor até o limite por operação e quantidade máxima de saques por dia."
    ),
    responses=_respostas,
)
async def sacar(dados: Movimentacao, cliente: ClienteAtual, session: Sessao):
    return await service.sacar(session, cliente.id, dados.conta_id, dados.valor, dados.descricao)


@router.post(
    "/transferencia",
    status_code=status.HTTP_201_CREATED,
    response_model=TransacaoPublica,
    summary="Transferir entre contas",
    description="Transfere de uma conta sua para qualquer conta pelo número. Operação atômica.",
    responses=_respostas,
)
async def transferir(dados: Transferencia, cliente: ClienteAtual, session: Sessao):
    return await service.transferir(
        session, cliente.id, dados.conta_origem_id, dados.conta_destino_numero, dados.valor, dados.descricao
    )
