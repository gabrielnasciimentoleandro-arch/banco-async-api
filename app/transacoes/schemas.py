from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.transacoes.models import TipoTransacao

Valor = Field(
    gt=0,
    max_digits=12,
    decimal_places=2,
    description="Valor positivo com até 2 casas decimais",
    examples=[150.00],
)


class Movimentacao(BaseModel):
    """Corpo de um depósito ou saque."""

    conta_id: int = Field(gt=0, examples=[1])
    valor: Decimal = Valor
    descricao: str | None = Field(default=None, max_length=140, examples=["Salário"])


class Transferencia(BaseModel):
    conta_origem_id: int = Field(gt=0, examples=[1])
    conta_destino_numero: str = Field(examples=["123456-7"], description="Número da conta de destino")
    valor: Decimal = Valor
    descricao: str | None = Field(default=None, max_length=140, examples=["Aluguel"])


class TransacaoPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conta_id: int
    tipo: TipoTransacao
    valor: Decimal
    saldo_apos: Decimal
    descricao: str | None
    realizada_em: datetime
