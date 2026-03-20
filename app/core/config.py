from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MyPage Service"
    app_env: str = "development"
    app_port: int = 8000

    # DATABASE_URL 직접 주입 또는 개별 컴포넌트로 조립 (ECS 환경)
    database_url: str = ""
    db_host: str = ""
    db_port: str = "5432"
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    history_database_url: str = ""

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.db_host and self.db_name and self.db_user:
            return (
                f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        raise ValueError("DATABASE_URL 또는 DB_HOST/DB_NAME/DB_USER/DB_PASSWORD/DB_PORT 환경변수가 필요합니다.")

    # Cognito
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    aws_region: str = "ap-northeast-2"

    # JWT fallback (dev only — used when cognito_user_pool_id is not set)
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket_name: str = ""
    s3_codef_bucket_name: str = ""

    # CODEF
    codef_client_id: str = ""
    codef_client_secret: str = ""
    codef_base_url: str = "https://development.codef.io"  # 운영: https://api.codef.io

    allowed_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
