import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")
    pinecone_index_name: str = "hackrx-documents"
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks: int = 100
    
    # Vector Search
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    # API Configuration
    api_token: str = "667efb9a18a1e0cb1dbc77a25fddc98c12849e980fc25cc9dea06eca61b1f4c8"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings() 