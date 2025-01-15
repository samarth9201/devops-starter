from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    1. First checks actual environment variables
    2. Then checks the .env file specified in Config
    3. Finally falls back to default values in the class
    """

    DATABASE_URL: str = "postgresql://postgres:postgres@database-1.clsewyi4449a.us-west-2.rds.amazonaws.com:5432/postgres"

    class Config:
        env_file = ".env"


settings = Settings()
