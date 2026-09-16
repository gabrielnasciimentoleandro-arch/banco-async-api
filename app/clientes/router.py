from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.clientes.models import Cliente
from app.clientes.schemas import ClienteCriar, ClientePublico, Token
from app.core.database import Sessao
from app.core.excecoes import Conflito
from app.core.seguranca import ClienteAtual, criar_token, gerar_hash, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/registrar",
    status_code=status.HTTP_201_CREATED,
    response_model=ClientePublico,
    summary="Cadastrar cliente",
    description="Cria um novo cliente. A senha é armazenada como hash Argon2.",
)
async def registrar(dados: ClienteCriar, session: Sessao):
    email = dados.email.lower()
    existe = await session.scalar(select(Cliente).where(Cliente.email == email))
    if existe:
        raise Conflito("Já existe um cliente cadastrado com este e-mail.")

    cliente = Cliente(nome=dados.nome, email=email, senha_hash=gerar_hash(dados.senha))
    session.add(cliente)
    await session.commit()
    await session.refresh(cliente)
    return cliente


@router.post(
    "/token",
    response_model=Token,
    summary="Login (obter token JWT)",
    description="Autentica com **e-mail** (campo `username`) e **senha** e retorna um token JWT Bearer.",
)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: Sessao):
    cliente = await session.scalar(select(Cliente).where(Cliente.email == form.username.lower()))
    if not cliente or not verificar_senha(form.password, cliente.senha_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=criar_token(cliente.id))


@router.get("/eu", response_model=ClientePublico, summary="Dados do cliente autenticado")
async def eu(cliente: ClienteAtual):
    return cliente
