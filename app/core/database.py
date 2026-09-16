from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config

engine = create_async_engine(config.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM."""


async def criar_tabelas() -> None:
    # Importa os modelos para registrá-los no metadata antes do create_all
    from app.clientes import models as _c  # noqa: F401
    from app.contas import models as _ct  # noqa: F401
    from app.transacoes import models as _t  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


Sessao = Annotated[AsyncSession, Depends(get_session)]
