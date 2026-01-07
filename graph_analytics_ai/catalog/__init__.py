"""
Analysis Catalog - Track and manage graph analytics executions over time.

This module provides comprehensive tracking of analysis executions, enabling:
- Historical analysis tracking
- Time-series analysis of graph metrics
- Lineage tracking from requirements to results
- Performance monitoring and alerting
- Multi-epoch comparison
- Advanced querying and pagination
- Impact analysis and coverage tracking
- Catalog management and maintenance

## Quick Start

```python
from graph_analytics_ai.catalog import (
    AnalysisCatalog,
    CatalogQueries,
    LineageTracker,
    CatalogManager,
)
from graph_analytics_ai.catalog.storage import ArangoDBStorage

# Initialize catalog
storage = ArangoDBStorage(db)
catalog = AnalysisCatalog(storage)

# Create epoch
epoch = catalog.create_epoch(
    name="2026-01-analysis",
    tags=["production"]
)

# Track execution (automatic in workflows)
execution_id = catalog.track_execution(execution)

# Query with pagination
queries = CatalogQueries(storage)
result = queries.query_with_pagination(
    filter=ExecutionFilter(algorithm="pagerank"),
    page=1,
    page_size=20
)

# Analyze lineage
tracker = LineageTracker(storage)
lineage = tracker.get_complete_lineage(execution_id)
impact = tracker.analyze_impact("req-123", "requirement")

# Manage catalog
manager = CatalogManager(storage)
integrity = manager.validate_catalog_integrity()
manager.archive_old_epochs(older_than_days=180)
```

## Modules

- `catalog`: Main API for tracking and retrieval
- `queries`: Advanced querying with pagination and statistics
- `lineage`: Enhanced lineage tracking and impact analysis
- `management`: Maintenance and administrative operations
- `storage`: Storage backend implementations
- `models`: Data models for all catalog entities
- `exceptions`: Custom exception hierarchy
"""

from .catalog import AnalysisCatalog
from .models import (
    AnalysisExecution,
    AnalysisEpoch,
    ExtractedRequirements,
    GeneratedUseCase,
    AnalysisTemplate,
    GraphConfig,
    PerformanceMetrics,
    ResultSample,
    ExecutionStatus,
    EpochStatus,
    ExecutionFilter,
    EpochFilter,
    ExecutionLineage,
    RequirementTrace,
    CatalogStatistics,
)
from .exceptions import (
    CatalogError,
    StorageError,
    ValidationError,
    NotFoundError,
    DuplicateError,
)
from .queries import (
    CatalogQueries,
    SortOption,
    PaginationResult,
    TimeSeriesQuery,
    QueryStatistics,
)
from .lineage import (
    LineageTracker,
    LineageGraph,
    ImpactAnalysis,
    CoverageReport,
)
from .management import CatalogManager

__version__ = "1.0.0"

__all__ = [
    # Main class
    "AnalysisCatalog",
    # Core models
    "AnalysisExecution",
    "AnalysisEpoch",
    "ExtractedRequirements",
    "GeneratedUseCase",
    "AnalysisTemplate",
    "GraphConfig",
    "PerformanceMetrics",
    "ResultSample",
    # Enums
    "ExecutionStatus",
    "EpochStatus",
    # Filters
    "ExecutionFilter",
    "EpochFilter",
    # Lineage
    "ExecutionLineage",
    "RequirementTrace",
    # Statistics
    "CatalogStatistics",
    # Exceptions
    "CatalogError",
    "StorageError",
    "ValidationError",
    "NotFoundError",
    "DuplicateError",
    # Advanced query classes
    "CatalogQueries",
    "SortOption",
    "PaginationResult",
    "TimeSeriesQuery",
    "QueryStatistics",
    # Lineage tracking
    "LineageTracker",
    "LineageGraph",
    "ImpactAnalysis",
    "CoverageReport",
    # Management
    "CatalogManager",
]
