from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.contas.models import Conta
from app.contas.service import obter_conta_do_cliente
from app.core.config import config
from app.core.excecoes import NaoEncontrado, RegraDeNegocio
from app.transacoes.models import TipoTransacao, Transacao

_TIPOS_SAIDA = (TipoTransacao.SAQUE, TipoTransacao.TRANSFERENCIA_ENVIADA)


async def _creditar(session: AsyncSession, conta: Conta, valor: Decimal) -> Decimal:
    """Soma o valor ao saldo diretamente no banco e devolve o novo saldo."""
    novo_saldo = await session.scalar(
        update(Conta).where(Conta.id == conta.id).values(saldo=Conta.saldo + valor).returning(Conta.saldo)
    )
    conta.saldo = Decimal(str(novo_saldo))
    return conta.saldo


async def _debitar(session: AsyncSession, conta: Conta, valor: Decimal) -> Decimal:
    """
    Debita de forma atômica: o UPDATE só afeta a linha se o saldo ainda for suficiente
    no momento da escrita. Isso evita saldo negativo quando várias requisições
    concorrem pela mesma conta (condição de corrida).
    """
    if valor > config.limite_saque_valor:
        raise RegraDeNegocio(f"O valor excede o limite de R$ {config.limite_saque_valor:.2f} por operação.")

    inicio_do_dia = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    saques_hoje = await session.scalar(
        select(func.count(Transacao.id)).where(
            Transacao.conta_id == conta.id,
            Transacao.tipo.in_(_TIPOS_SAIDA),
            Transacao.realizada_em >= inicio_do_dia,
        )
    )
    if (saques_hoje or 0) >= config.limite_saques_diarios:
        raise RegraDeNegocio(
            f"Limite de {config.limite_saques_diarios} saques/transferências diários atingido."
        )

    novo_saldo = await session.scalar(
        update(Conta)
        .where(Conta.id == conta.id, Conta.saldo >= valor)
        .values(saldo=Conta.saldo - valor)
        .returning(Conta.saldo)
    )
    if novo_saldo is None:
        await session.refresh(conta)
        raise RegraDeNegocio(f"Saldo insuficiente. Saldo atual: R$ {Decimal(conta.saldo):.2f}.")

    conta.saldo = Decimal(str(novo_saldo))
    return conta.saldo


def _nova_transacao(conta: Conta, tipo: TipoTransacao, valor: Decimal, descricao: str | None) -> Transacao:
    return Transacao(conta_id=conta.id, tipo=tipo, valor=valor, saldo_apos=conta.saldo, descricao=descricao)


async def depositar(
    session: AsyncSession, cliente_id: int, conta_id: int, valor: Decimal, descricao: str | None
) -> Transacao:
    conta = await obter_conta_do_cliente(session, conta_id, cliente_id)
    await _creditar(session, conta, valor)
    transacao = _nova_transacao(conta, TipoTransacao.DEPOSITO, valor, descricao)
    session.add(transacao)
    await session.commit()
    await session.refresh(transacao)
    return transacao


async def sacar(
    session: AsyncSession, cliente_id: int, conta_id: int, valor: Decimal, descricao: str | None
) -> Transacao:
    conta = await obter_conta_do_cliente(session, conta_id, cliente_id)
    await _debitar(session, conta, valor)
    transacao = _nova_transacao(conta, TipoTransacao.SAQUE, valor, descricao)
    session.add(transacao)
    await session.commit()
    await session.refresh(transacao)
    return transacao


async def transferir(
    session: AsyncSession,
    cliente_id: int,
    origem_id: int,
    destino_numero: str,
    valor: Decimal,
    descricao: str | None,
) -> Transacao:
    origem = await obter_conta_do_cliente(session, origem_id, cliente_id)
    destino = await session.scalar(select(Conta).where(Conta.numero == destino_numero))
    if destino is None:
        raise NaoEncontrado("Conta de destino")
    if destino.id == origem.id:
        raise RegraDeNegocio("A conta de destino deve ser diferente da conta de origem.")

    # Débito e crédito na mesma transação de banco: ou ambos persistem, ou nenhum.
    await _debitar(session, origem, valor)
    await _creditar(session, destino, valor)
    saida = _nova_transacao(
        origem, TipoTransacao.TRANSFERENCIA_ENVIADA, valor, descricao or f"Para conta {destino.numero}"
    )
    entrada = _nova_transacao(
        destino, TipoTransacao.TRANSFERENCIA_RECEBIDA, valor, descricao or f"De conta {origem.numero}"
    )
    session.add_all([saida, entrada])
    await session.commit()
    await session.refresh(saida)
    return saida
