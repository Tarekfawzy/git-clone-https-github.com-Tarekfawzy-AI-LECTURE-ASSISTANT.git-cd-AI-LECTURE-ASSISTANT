import whisper
from typing import Dict, Any
from .config import Config

class AudioTranscriber:
    """Handle audio transcription using OpenAI Whisper."""
    
    def __init__(self, config: Config):
        self.config = config
        self.model = whisper.load_model(config.whisper_model)
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary containing transcription results
        """
        language_code = self.config.get_language_code()
        
        # Transcribe with Whisper
        result = self.model.transcribe(
            audio_path,
            language=language_code if language_code != "en" else None,
            word_level_timings=True
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"],
            "language": result["language"]
        }
