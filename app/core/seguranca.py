from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select

from app.clientes.models import Cliente
from app.core.config import config
from app.core.database import Sessao

_hasher = PasswordHash.recommended()  # Argon2id
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def gerar_hash(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, hash_: str) -> bool:
    return _hasher.verify(senha, hash_)


def criar_token(cliente_id: int) -> str:
    agora = datetime.now(UTC)
    payload = {
        "sub": str(cliente_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=config.token_expira_minutos),
    }
    return jwt.encode(payload, config.secret_key, algorithm=config.algoritmo)


async def obter_cliente_atual(token: Annotated[str, Depends(oauth2_scheme)], session: Sessao) -> Cliente:
    erro = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algoritmo])
        cliente_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro

    cliente = await session.scalar(select(Cliente).where(Cliente.id == cliente_id))
    if cliente is None:
        raise erro
    return cliente


ClienteAtual = Annotated[Cliente, Depends(obter_cliente_atual)]
