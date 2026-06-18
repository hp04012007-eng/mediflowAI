import os

class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "mediflow_secret_key"
    )

    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        "database/hospital.db"
    )

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )