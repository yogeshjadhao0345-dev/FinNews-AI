import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Settings:
    def __init__(self):
        self.reload()

    def reload(self):
        load_dotenv(BASE_DIR / ".env", override=True)
        self.news_api_key: str = os.getenv("NEWS_API_KEY", "").strip()
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
        self.host: str = os.getenv("HOST", "127.0.0.1")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.cache_ttl: int = int(os.getenv("CACHE_TTL_SECONDS", "900"))

    def update_keys(self, news_api_key: str | None = None, gemini_api_key: str | None = None, openai_api_key: str | None = None):
        if news_api_key is not None:
            self.news_api_key = news_api_key.strip()
            os.environ["NEWS_API_KEY"] = self.news_api_key
        if gemini_api_key is not None:
            self.gemini_api_key = gemini_api_key.strip()
            os.environ["GEMINI_API_KEY"] = self.gemini_api_key
        if openai_api_key is not None:
            self.openai_api_key = openai_api_key.strip()
            os.environ["OPENAI_API_KEY"] = self.openai_api_key

        # Persist to .env
        env_path = BASE_DIR / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        keys_present = set()
        new_lines = []
        for line in lines:
            if line.startswith("NEWS_API_KEY="):
                new_lines.append(f"NEWS_API_KEY={self.news_api_key}\n")
                keys_present.add("NEWS_API_KEY")
            elif line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={self.gemini_api_key}\n")
                keys_present.add("GEMINI_API_KEY")
            elif line.startswith("OPENAI_API_KEY="):
                new_lines.append(f"OPENAI_API_KEY={self.openai_api_key}\n")
                keys_present.add("OPENAI_API_KEY")
            else:
                new_lines.append(line)

        if "NEWS_API_KEY" not in keys_present:
            new_lines.append(f"NEWS_API_KEY={self.news_api_key}\n")
        if "GEMINI_API_KEY" not in keys_present:
            new_lines.append(f"GEMINI_API_KEY={self.gemini_api_key}\n")
        if "OPENAI_API_KEY" not in keys_present:
            new_lines.append(f"OPENAI_API_KEY={self.openai_api_key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    @property
    def has_news_api(self) -> bool:
        return bool(self.news_api_key and not self.news_api_key.startswith("your_"))

    @property
    def has_gemini_api(self) -> bool:
        return bool(self.gemini_api_key and not self.gemini_api_key.startswith("your_"))

    @property
    def has_openai_api(self) -> bool:
        return bool(self.openai_api_key and not self.openai_api_key.startswith("your_"))

settings = Settings()
