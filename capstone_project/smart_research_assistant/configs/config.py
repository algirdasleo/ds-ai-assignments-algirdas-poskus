from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: str
    connection_string: str
    tavily_api_key: str

    class Config:
        env_file = ".env"
