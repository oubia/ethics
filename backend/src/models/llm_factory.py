import time
import logging
from src.utils.prompts.prompt import general_prompt

class LLMFactory:
    def __init__(self, model_name: str, system_prompt: str | None = None, timeout: int = 600):
        self.model_name = model_name.lower()
        self.system_prompt = system_prompt or general_prompt
        self.timeout = timeout  # Default 10 minutes for long inference times
        if self.model_name == "llama":
            self.llm = self._init_llama_with_retry()
        else:
            raise ValueError(f"Unsupported model name: {model_name}. Supported models: 'llama'.")
    
    def _init_llama_with_retry(self):
        from langchain_ollama import OllamaLLM
        from src.config.settings import OLLAMA_LLM_ENDPOINT, OLLAMA_REQUEST_TIMEOUT
        
        # Use timeout from settings or fall back to instance timeout
        timeout = OLLAMA_REQUEST_TIMEOUT if OLLAMA_REQUEST_TIMEOUT else self.timeout
        
        try:
            logging.info("Attempting to initialize Llama LLM at endpoint: %s with timeout: %ds", 
                        OLLAMA_LLM_ENDPOINT, timeout)
            llm = OllamaLLM(
                model="llama3.2:latest",  
                temperature=0.2,
                streaming=True,
                verbose=True,
                system=self.system_prompt,
                base_url=OLLAMA_LLM_ENDPOINT,
                timeout=timeout  # Set explicit timeout
            )
            logging.info("Llama LLM initialized successfully with timeout: %ds", timeout)
            return llm
        except Exception as e:
            logging.error("Error initializing Llama LLM: %s", str(e))
            raise
    
    def get_llm(self):
        return self.llm