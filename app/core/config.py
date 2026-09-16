from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./banco.db"
    secret_key: str = "chave-insegura-somente-para-desenvolvimento-local-0123456789"
    algoritmo: str = "HS256"
    token_expira_minutos: int = 60
    limite_saque_valor: Decimal = Decimal("500.00")
    limite_saques_diarios: int = 3


config = Config()
