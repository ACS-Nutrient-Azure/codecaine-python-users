from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MyPage Service"
    app_env: str = "development"
    app_port: int = 8000

    database_url: str
    history_database_url: str = ""

    # Cognito
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    aws_region: str = "ap-northeast-2"

    # JWT fallback (dev only — used when cognito_user_pool_id is not set)
    jwt_secret_key: str = "dev-secret-key"
    jwt_algorithm: str = "HS256"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""

    # CODEF
    codef_client_id: str = ""
    codef_client_secret: str = ""

    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
