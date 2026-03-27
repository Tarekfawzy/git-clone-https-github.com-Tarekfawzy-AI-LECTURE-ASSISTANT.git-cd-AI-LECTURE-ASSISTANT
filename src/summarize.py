from typing import Optional
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .config import Config

class TextSummarizer:
    """Generate summaries using LLM."""
    
    def __init__(self, config: Config):
        self.config = config
        
        if config.llm_provider == "openai":
            self.llm = OpenAI(
                openai_api_key=config.openai_api_key,
                temperature=0.5,
                max_tokens=1000
            )
        else:
            # For Ollama
            from langchain.llms import Ollama
            self.llm = Ollama(
                base_url=config.ollama_base_url,
                model=config.ollama_model,
                temperature=0.5
            )
    
    def summarize(self, text: str, style: str = "Brief (Key Points)") -> str:
        """
        Generate summary of the text.
        
        Args:
            text: Text to summarize
            style: Summary style (Brief, Detailed, or Bullet Points)
            
        Returns:
            Summarized text
        """
        
        style_prompts = {
            "Brief (Key Points)": "Provide a brief summary in 3-5 key points.",
            "Detailed (Full Summary)": "Provide a detailed summary covering all main topics.",
            "Bullet Points": "Summarize as a list of bullet points."
        }
        
        prompt_template = PromptTemplate(
            input_variables=["text", "style_instruction"],
            template="Summarize the following lecture transcript:\n\n{text}\n\nRequirement: {style_instruction}"
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        
        result = chain.run(
            text=text[:2000],  # Limit to 2000 chars to avoid token limits
            style_instruction=style_prompts.get(style, style_prompts["Brief (Key Points)"])
        )
        
        return result.strip()
