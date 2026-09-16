import secrets
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.contas.models import Conta
from app.core.excecoes import NaoEncontrado, SemPermissao
from app.transacoes.models import TipoTransacao, Transacao


async def _gerar_numero_unico(session: AsyncSession) -> str:
    while True:
        numero = f"{secrets.randbelow(10**6):06d}-{secrets.randbelow(10)}"
        if not await session.scalar(select(Conta.id).where(Conta.numero == numero)):
            return numero


async def abrir_conta(session: AsyncSession, cliente_id: int) -> Conta:
    conta = Conta(numero=await _gerar_numero_unico(session), cliente_id=cliente_id)
    session.add(conta)
    await session.commit()
    await session.refresh(conta)
    return conta


async def listar_contas(session: AsyncSession, cliente_id: int) -> list[Conta]:
    resultado = await session.scalars(select(Conta).where(Conta.cliente_id == cliente_id).order_by(Conta.id))
    return list(resultado)


async def obter_conta_do_cliente(
    session: AsyncSession, conta_id: int, cliente_id: int, *, com_transacoes: bool = False
) -> Conta:
    """Busca a conta e garante que pertence ao cliente autenticado."""
    stmt = select(Conta).where(Conta.id == conta_id)
    if com_transacoes:
        stmt = stmt.options(selectinload(Conta.transacoes))
    conta = await session.scalar(stmt)
    if conta is None:
        raise NaoEncontrado("Conta")
    if conta.cliente_id != cliente_id:
        raise SemPermissao("Esta conta pertence a outro cliente.")
    return conta


async def montar_extrato(session: AsyncSession, conta_id: int, cliente_id: int) -> dict:
    conta = await obter_conta_do_cliente(session, conta_id, cliente_id, com_transacoes=True)

    async def soma(tipo: TipoTransacao) -> Decimal:
        valor = await session.scalar(
            select(func.coalesce(func.sum(Transacao.valor), 0)).where(
                Transacao.conta_id == conta_id, Transacao.tipo == tipo
            )
        )
        return Decimal(str(valor))

    return {
        "conta": conta,
        "total_depositos": await soma(TipoTransacao.DEPOSITO),
        "total_saques": await soma(TipoTransacao.SAQUE),
        "transacoes": conta.transacoes,
    }
