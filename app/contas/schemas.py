from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.transacoes.schemas import TransacaoPublica


class ContaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    agencia: str
    saldo: Decimal
    criada_em: datetime


class Extrato(BaseModel):
    conta: ContaPublica
    total_depositos: Decimal = Field(description="Soma de todos os depósitos recebidos")
    total_saques: Decimal = Field(description="Soma de todos os saques realizados")
    transacoes: list[TransacaoPublica]
