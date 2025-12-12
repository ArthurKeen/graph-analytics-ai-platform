"""
GAE Template Generation Module

Generates ArangoDB Graph Analytics Engine (GAE) AnalysisConfig templates from use cases.
Converts high-level use case descriptions into executable GAE job configurations.
"""

from .generator import TemplateGenerator, generate_template
from .models import (
    AnalysisTemplate,
    AlgorithmType,
    EngineSize,
    TemplateConfig
)

__all__ = [
    "TemplateGenerator",
    "generate_template",
    "AnalysisTemplate",
    "AlgorithmType",
    "EngineSize",
    "TemplateConfig",
]

