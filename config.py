"""Configuration management using pydantic-settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AgentConfig(BaseSettings):
    """Configuration for intelligent agents."""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # Dual Model Configuration
    openai_reasoning_model: str = Field(
        default="gpt-4-mini",
        description="Model for complex reasoning tasks (slower, more capable)"
    )
    openai_inference_model: str = Field(
        default="gpt-4-nano",
        description="Model for simple inference tasks (faster, cheaper)"
    )
    
    # Agent Configuration
    max_iterations: int = Field(default=10, ge=1, description="Maximum iterations for agent loop")
    verbose: bool = Field(default=False, description="Enable verbose output")
    
    # Conversation Compaction Configuration
    compact_after_loops: int = Field(
        default=3,
        ge=1,
        description="Number of conversation loops after which to trigger compaction"
    )
    
    compact_context_threshold: int = Field(
        default=50000,
        ge=1000,
        description="Context length (in tokens) after which to trigger compaction"
    )
    
    # API Keys
    alphavantage_api_key: str = Field(default='LQZ843E6GUXS9563', description="Alpha Vantage API key for stock data")
    marketaux_api_key: str = Field(defailt='CnnCfqBR021wPSKkMUc6ChxOUocZmbXfDYglCtmJ', description="Marketaux API key for financial news and market data")

