"""
GAE Analysis Report Generation Module

Generates actionable intelligence reports from GAE analysis results.
Provides insights, recommendations, execution metrics, and multiple output formats.
"""

from .generator import ReportGenerator, generate_report
from .models import (
    AnalysisReport,
    ReportSection,
    Insight,
    Recommendation,
    ReportFormat
)
from .config import (
    ReportConfig,
    WorkflowReportConfig,
    ReportSection as ConfigReportSection
)
from .formatter import ExecutionReportFormatter

__all__ = [
    "ReportGenerator",
    "generate_report",
    "AnalysisReport",
    "ReportSection",
    "Insight",
    "Recommendation",
    "ReportFormat",
    "ReportConfig",
    "WorkflowReportConfig",
    "ExecutionReportFormatter",
]

