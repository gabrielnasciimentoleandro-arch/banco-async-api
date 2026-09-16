from fastapi import HTTPException, status


class NaoEncontrado(HTTPException):
    def __init__(self, recurso: str = "Recurso"):
        super().__init__(status.HTTP_404_NOT_FOUND, f"{recurso} não encontrado(a).")


class SemPermissao(HTTPException):
    def __init__(self, detalhe: str = "Você não tem permissão para acessar este recurso."):
        super().__init__(status.HTTP_403_FORBIDDEN, detalhe)


class RegraDeNegocio(HTTPException):
    """Operação válida sintaticamente, mas que viola uma regra do banco (ex.: saldo insuficiente)."""

    def __init__(self, detalhe: str):
        super().__init__(422, detalhe)


class Conflito(HTTPException):
    def __init__(self, detalhe: str):
        super().__init__(status.HTTP_409_CONFLICT, detalhe)
