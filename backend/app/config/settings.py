"""
Configuration settings for Virtuals ACP integration.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # API configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Floww Virtuals ACP"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Floww AI Agents integration with Virtuals ACP"

    # Virtuals ACP Integration
    VIRTUALS_ACP_CONTRACT_ADDRESS: Optional[str] = Field(
        default=None,
        description="VirtualsACP contract address on Base"
    )
    ALCHEMY_RPC_URL: Optional[str] = Field(
        default=None,
        description="Alchemy RPC URL for Base network"
    )
    BACKEND_PRIVATE_KEY: Optional[str] = Field(
        default=None,
        description="Backend private key for signing transactions"
    )

    # Network configuration
    CHAIN_ID: int = Field(default=8453, description="Chain ID (8453 for Base Mainnet, 84532 for Base Sepolia)")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Global settings instance
settings = Settings()