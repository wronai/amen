"""
amen: Configuration
Environment-based configuration for all components.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # General
    debug: bool = False
    log_level: str = "INFO"
    
    # Web server
    host: str = "0.0.0.0"
    port: int = 8080
    
    # AI Gateway
    ai_enabled: bool = True
    default_model: str = "llama3.2"
    max_model_params: float = 12.0
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120
    
    # Optional API keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    
    # Execution
    docker_enabled: bool = True
    workspace_dir: str = "/tmp/amen"
    
    def __post_init__(self):
        """Load from environment variables."""
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", self.port))
        
        self.ai_enabled = os.getenv("AI_ENABLED", "true").lower() == "true"
        self.default_model = os.getenv("DEFAULT_MODEL", self.default_model)
        self.max_model_params = float(os.getenv("MAX_MODEL_PARAMS", self.max_model_params))
        
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.ollama_base_url)
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", self.ollama_timeout))
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        self.docker_enabled = os.getenv("DOCKER_ENABLED", "true").lower() == "true"
        self.workspace_dir = os.getenv("WORKSPACE_DIR", self.workspace_dir)


# Global config instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create application config."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def configure(**kwargs) -> AppConfig:
    """Configure application with custom settings."""
    global _config
    _config = AppConfig(**kwargs)
    return _config
