from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str

    # Automatically tells Pydantic to read from the .env file in the root folder
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Initialize a global settings object to import anywhere
settings = Settings()
