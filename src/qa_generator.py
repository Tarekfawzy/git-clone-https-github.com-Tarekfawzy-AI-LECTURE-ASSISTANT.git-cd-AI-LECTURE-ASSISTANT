from typing import Dict, List, Any
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .config import Config
import re

class QAGenerator:
    """Generate questions and answers from text."""
    
    def __init__(self, config: Config):
        self.config = config
        
        if config.llm_provider == "openai":
            self.llm = OpenAI(
                openai_api_key=config.openai_api_key,
                temperature=0.7,
                max_tokens=1500
            )
        else:
            from langchain.llms import Ollama
            self.llm = Ollama(
                base_url=config.ollama_base_url,
                model=config.ollama_model,
                temperature=0.7
            )
    
    def generate_qa(self, text: str, num_questions: int = 5) -> Dict[str, Any]:
        """
        Generate Q&A pairs from text.
        
        Args:
            text: Text to generate Q&A from
            num_questions: Number of questions to generate
            
        Returns:
            Dictionary with Q&A pairs and keywords
        """
        
        # Generate questions and answers
        qa_prompt = PromptTemplate(
            input_variables=["text", "num_questions"],
            template="""Based on the following lecture transcript, generate {num_questions} important questions with detailed answers.
            
Format each Q&A as:
Q: [Question]
A: [Answer]

Transcript:
{text}"""
        )
        
        chain = LLMChain(llm=self.llm, prompt=qa_prompt)
        qa_text = chain.run(
            text=text[:2000],
            num_questions=num_questions
        )
        
        # Parse Q&A pairs
        qa_pairs = self._parse_qa_text(qa_text)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        return {
            "qa_pairs": qa_pairs,
            "keywords": keywords
        }
    
    def _parse_qa_text(self, qa_text: str) -> List[Dict[str, str]]:
        """Parse Q&A text into structured format."""
        qa_pairs = []
        
        # Split by Q: pattern
        questions = re.split(r'Q\d*:', qa_text)
        
        for q_block in questions[1:]:  # Skip first empty split
            lines = q_block.strip().split('\n')
            if len(lines) >= 2:
                question = lines[0].strip()
                answer_lines = [l.strip() for l in lines[1:] if l.strip() and not l.startswith('Q')]
                answer = ' '.join(answer_lines)
                
                if question and answer:
                    qa_pairs.append({
                        "question": question,
                        "answer": answer[:500]  # Limit answer length
                    })
        
        return qa_pairs[:5]  # Return top 5
    
    def _extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract important keywords from text."""
        from collections import Counter
        import nltk
        from nltk.corpus import stopwords
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        stop_words = set(stopwords.words('english'))
        
        # Simple keyword extraction
        words = text.lower().split()
        words = [w.strip('.,!?;:') for w in words]
        words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        word_freq = Counter(words)
        keywords = [word for word, _ in word_freq.most_common(num_keywords)]
        
        return keywords
