from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.clientes.models import Cliente
    from app.transacoes.models import Transacao


class Conta(Base):
    __tablename__ = "contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    agencia: Mapped[str] = mapped_column(String(4), default="0001")
    saldo: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    criada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cliente: Mapped["Cliente"] = relationship(back_populates="contas")
    transacoes: Mapped[list["Transacao"]] = relationship(
        back_populates="conta", cascade="all, delete-orphan", order_by="Transacao.id.desc()"
    )
