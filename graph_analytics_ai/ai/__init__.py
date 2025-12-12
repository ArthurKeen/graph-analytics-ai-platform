"""
AI-assisted workflow module for Graph Analytics AI.

This module provides AI-powered features for automating graph analytics workflows:
- Automated PRD generation from business requirements
- Use case generation based on graph schema
- Analysis template generation
- Actionable intelligence reporting

All AI features are OPTIONAL and require explicit opt-in. The core library
works perfectly fine without this module.

Example:
    >>> from graph_analytics_ai.ai import create_llm_provider
    >>> 
    >>> # Create LLM provider
    >>> provider = create_llm_provider(
    ...     provider="openrouter",
    ...     model="google/gemini-2.5-flash"
    ... )
    >>> 
    >>> # Use for generation
    >>> response = provider.generate("What is graph analytics?")
    >>> print(response.content)

Note:
    AI features require:
    - LLM API key (OpenRouter, OpenAI, or Anthropic)
    - AI_WORKFLOW_ENABLED=true in environment
    - Additional dependencies: pip install graph-analytics-ai[ai]
"""

# LLM providers
from .llm import (
    LLMProvider,
    LLMConfig,
    LLMResponse,
    LLMProviderError,
    create_llm_provider,
    get_default_provider
)

__version__ = "0.1.0"  # AI module version (separate from core library)

__all__ = [
    # LLM providers
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "LLMProviderError",
    "create_llm_provider",
    "get_default_provider",
]
