from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 앱 기본 설정
    app_name: str = "MyPage Service"
    app_env: str = "development"
    app_port: int = 8000

    # 데이터베이스
    database_url: str

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-northeast-2"
    s3_bucket_name: str = ""

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


# 앱 전체에서 이걸 import해서 사용
settings = Settings()
