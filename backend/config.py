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

    # AI Models Configuration
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "google/flan-t5-base")
    NLI_MODEL_NAME: str = os.getenv("NLI_MODEL_NAME", "cross-encoder/nli-deberta-v3-xsmall")

    # Benchmark knowledge file
    BENCHMARK_DATA_PATH: Path = BASE_DIR / "backend" / "data" / "benchmark_facts.json"

settings = Settings()
