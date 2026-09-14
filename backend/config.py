import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # AI Models Configuration (optimized for Render 512MB RAM free tier)
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "google/flan-t5-small")
    NLI_MODEL_NAME: str = os.getenv("NLI_MODEL_NAME", "cross-encoder/nli-deberta-v3-xsmall")
    ENABLE_LLM_DOWNLOAD: bool = os.getenv("ENABLE_LLM_DOWNLOAD", "false").lower() == "true"
    ENABLE_NLI_DOWNLOAD: bool = os.getenv("ENABLE_NLI_DOWNLOAD", "true").lower() == "true"

    # Benchmark knowledge file
    BENCHMARK_DATA_PATH: Path = BASE_DIR / "backend" / "data" / "benchmark_facts.json"

settings = Settings()
