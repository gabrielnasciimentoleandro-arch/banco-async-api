import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.contas.models import Conta


class TipoTransacao(str, enum.Enum):
    DEPOSITO = "deposito"
    SAQUE = "saque"
    TRANSFERENCIA_ENVIADA = "transferencia_enviada"
    TRANSFERENCIA_RECEBIDA = "transferencia_recebida"


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), index=True)
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao, name="tipo_transacao"))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    saldo_apos: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    descricao: Mapped[str | None] = mapped_column(String(140))
    realizada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conta: Mapped["Conta"] = relationship(back_populates="transacoes")
