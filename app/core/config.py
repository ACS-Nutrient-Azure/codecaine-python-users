from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MyPage Service"
    app_env: str = "development"
    app_port: int = 8000

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: str = ""

    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
