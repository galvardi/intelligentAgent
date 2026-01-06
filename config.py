"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AgentConfig(BaseSettings):
    """Configuration for intelligent agents."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # Dual Model Configuration
    openai_reasoning_model: str = Field(
        default="gpt-5-mini",
        description="Model for complex reasoning tasks (slower, more capable)"
    )
    openai_inference_model: str = Field(
        default="gpt-5-nano",
        description="Model for simple inference tasks (faster, cheaper)"
    )
    
    # Agent Configuration
    max_iterations: int = Field(default=10, ge=1, description="Maximum iterations for agent loop")
    verbose: bool = Field(default=False, description="Enable verbose output")

