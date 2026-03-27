import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for AI Lecture Assistant."""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        language: str = "English",
        enable_diarization: bool = False,
        llm_provider: str = "openai"
    ):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.language = language
        self.enable_diarization = enable_diarization
        self.llm_provider = llm_provider.lower()
        
        # Whisper model size
        self.whisper_model = os.getenv("WHISPER_MODEL", "base")
        
        # Ollama settings
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        
        # AssemblyAI settings (optional)
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
        
        # Validate configuration
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI provider")
    
    def get_language_code(self) -> str:
        """Map language name to language code."""
        language_map = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Arabic": "ar",
            "Chinese": "zh",
            "Japanese": "ja",
            "Portuguese": "pt",
            "Russian": "ru",
            "Hindi": "hi"
        }
        return language_map.get(self.language, "en")
