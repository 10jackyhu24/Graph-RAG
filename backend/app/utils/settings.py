import os


class Settings:
    def __init__(self) -> None:
        self.data_dir = os.getenv("DATA_DIR", "./app/data")

        self.llm_provider = os.getenv("LLM_PROVIDER")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:8b")

        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        self.postgres_dsn = os.getenv("POSTGRES_DSN", "postgresql://graph:graph@localhost:5435/graph")

        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")

        self.chroma_base_dir = os.getenv("CHROMA_DIR", os.path.join(self.data_dir, "chroma"))
        self.chroma_http_url = os.getenv("CHROMA_HTTP_URL")
        self.embeddings_provider = os.getenv("EMBEDDINGS_PROVIDER", "ollama").lower()
        self.st_embeddings_model = os.getenv("ST_EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
        self.poppler_path = os.getenv("POPPLER_PATH")
        self.tesseract_path = os.getenv("TESSERACT_PATH")
        self.ocr_agent = os.getenv("OCR_AGENT")
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        self.asr_backend = os.getenv("ASR_BACKEND", "auto").lower()
        self.whisper_device = os.getenv("WHISPER_DEVICE", "cpu")
        self.whisper_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    @property
    def resolved_llm_provider(self) -> str:
        if self.llm_provider:
            return self.llm_provider
        if self.deepseek_api_key:
            return "deepseek"
        return "ollama"


settings = Settings()
