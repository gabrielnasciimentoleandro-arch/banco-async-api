from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCriar(BaseModel):
    nome: str = Field(min_length=2, max_length=120, examples=["Maria Silva"])
    email: EmailStr = Field(examples=["maria@email.com"])
    senha: str = Field(min_length=6, max_length=72, examples=["senha123"])


class ClientePublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    criado_em: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
