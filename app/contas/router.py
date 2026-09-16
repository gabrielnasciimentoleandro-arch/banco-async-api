from fastapi import APIRouter, status

from app.contas import service
from app.contas.schemas import ContaPublica, Extrato
from app.core.database import Sessao
from app.core.seguranca import ClienteAtual

router = APIRouter(prefix="/contas", tags=["Contas"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ContaPublica,
    summary="Abrir conta corrente",
    description="Abre uma nova conta corrente (saldo zero) para o cliente autenticado. O número é gerado automaticamente.",
)
async def abrir_conta(cliente: ClienteAtual, session: Sessao):
    return await service.abrir_conta(session, cliente.id)


@router.get("", response_model=list[ContaPublica], summary="Listar minhas contas")
async def listar_contas(cliente: ClienteAtual, session: Sessao):
    return await service.listar_contas(session, cliente.id)


@router.get(
    "/{conta_id}",
    response_model=ContaPublica,
    summary="Consultar saldo da conta",
    responses={403: {"description": "Conta de outro cliente"}, 404: {"description": "Conta não encontrada"}},
)
async def consultar_conta(conta_id: int, cliente: ClienteAtual, session: Sessao):
    return await service.obter_conta_do_cliente(session, conta_id, cliente.id)


@router.get(
    "/{conta_id}/extrato",
    response_model=Extrato,
    summary="Exibir extrato",
    description="Retorna saldo atual, totais de depósitos/saques e todas as transações, da mais recente para a mais antiga.",
    responses={403: {"description": "Conta de outro cliente"}, 404: {"description": "Conta não encontrada"}},
)
async def extrato(conta_id: int, cliente: ClienteAtual, session: Sessao):
    return await service.montar_extrato(session, conta_id, cliente.id)
