"""
Advanced query operations for the Analysis Catalog.

Provides sophisticated filtering, sorting, aggregation, and pagination
capabilities for catalog queries.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .models import (
    AnalysisExecution,
    ExecutionFilter,
    ExecutionStatus,
)
from .storage.base import StorageBackend
from .exceptions import QueryError

logger = logging.getLogger(__name__)


@dataclass
class SortOption:
    """Sorting configuration for queries."""

    field: str
    """Field to sort by (e.g., 'timestamp', 'execution_time_seconds')."""

    ascending: bool = False
    """Sort order: False for descending (newest first), True for ascending."""


@dataclass
class PaginationResult:
    """Paginated query results."""

    items: List[Any]
    """List of items in this page."""

    total_count: int
    """Total number of items matching filter."""

    page: int
    """Current page number (1-based)."""

    page_size: int
    """Number of items per page."""

    total_pages: int
    """Total number of pages."""

    has_next: bool
    """Whether there are more pages."""

    has_previous: bool
    """Whether there are previous pages."""


@dataclass
class TimeSeriesQuery:
    """Configuration for time-series queries."""

    metric: str
    """Metric to query (e.g., 'execution_time_seconds', 'result_count')."""

    algorithm: Optional[str] = None
    """Filter by specific algorithm."""

    start_date: Optional[datetime] = None
    """Start of time range."""

    end_date: Optional[datetime] = None
    """End of time range."""

    interval: Optional[str] = None
    """Aggregation interval: 'hour', 'day', 'week', 'month'."""

    aggregation: str = "avg"
    """Aggregation function: 'avg', 'sum', 'min', 'max', 'count'."""


@dataclass
class QueryStatistics:
    """Statistics about a query result set."""

    total_count: int
    """Total number of results."""

    algorithms: Dict[str, int]
    """Count by algorithm."""

    statuses: Dict[str, int]
    """Count by status."""

    date_range: Optional[Tuple[datetime, datetime]]
    """Earliest and latest timestamp."""

    total_execution_time: float
    """Sum of execution times."""

    total_cost: float
    """Sum of costs."""

    avg_execution_time: float
    """Average execution time."""

    avg_cost: float
    """Average cost."""


class CatalogQueries:
    """
    Advanced query operations for the catalog.

    Provides methods for complex filtering, sorting, pagination,
    and aggregation of catalog data.
    """

    def __init__(self, storage: StorageBackend):
        """
        Initialize query operations.

        Args:
            storage: Storage backend
        """
        self.storage = storage

    def query_with_pagination(
        self,
        filter: Optional[ExecutionFilter] = None,
        sort: Optional[SortOption] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginationResult:
        """
        Query executions with pagination support.

        Args:
            filter: Filter criteria
            sort: Sort configuration
            page: Page number (1-based)
            page_size: Items per page

        Returns:
            PaginationResult with items and metadata

        Example:
            >>> result = queries.query_with_pagination(
            ...     filter=ExecutionFilter(algorithm="pagerank"),
            ...     page=1,
            ...     page_size=20
            ... )
            >>> print(f"Page {result.page} of {result.total_pages}")
            >>> for execution in result.items:
            ...     print(execution.algorithm)
        """
        if page < 1:
            raise QueryError("Page number must be >= 1")
        if page_size < 1 or page_size > 1000:
            raise QueryError("Page size must be between 1 and 1000")

        # Get total count (for pagination metadata)
        # Note: This requires a count query - implementation depends on storage
        # For now, we'll fetch all and count (inefficient, but works)
        all_items = self.storage.query_executions(filter, limit=10000, offset=0)
        total_count = len(all_items)

        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size

        # Get page items
        if sort:
            # Sort in memory (could be optimized with storage-level sorting)
            all_items.sort(
                key=lambda x: self._get_sort_key(x, sort.field),
                reverse=not sort.ascending,
            )

        items = all_items[offset : offset + page_size]

        return PaginationResult(
            items=items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

    def get_statistics(
        self, filter: Optional[ExecutionFilter] = None
    ) -> QueryStatistics:
        """
        Get statistics about executions matching filter.

        Args:
            filter: Filter criteria

        Returns:
            QueryStatistics with counts and aggregations

        Example:
            >>> stats = queries.get_statistics(
            ...     filter=ExecutionFilter(start_date=datetime(2026, 1, 1))
            ... )
            >>> print(f"Total: {stats.total_count}")
            >>> print(f"Avg time: {stats.avg_execution_time}s")
        """
        executions = self.storage.query_executions(filter, limit=10000, offset=0)

        if not executions:
            return QueryStatistics(
                total_count=0,
                algorithms={},
                statuses={},
                date_range=None,
                total_execution_time=0.0,
                total_cost=0.0,
                avg_execution_time=0.0,
                avg_cost=0.0,
            )

        # Calculate statistics
        algorithms: Dict[str, int] = {}
        statuses: Dict[str, int] = {}
        total_execution_time = 0.0
        total_cost = 0.0
        min_timestamp = executions[0].timestamp
        max_timestamp = executions[0].timestamp

        for execution in executions:
            # Count by algorithm
            algorithms[execution.algorithm] = algorithms.get(execution.algorithm, 0) + 1

            # Count by status
            status_str = execution.status.value
            statuses[status_str] = statuses.get(status_str, 0) + 1

            # Sum metrics
            total_execution_time += execution.performance_metrics.execution_time_seconds
            if execution.performance_metrics.cost_usd:
                total_cost += execution.performance_metrics.cost_usd

            # Track date range
            if execution.timestamp < min_timestamp:
                min_timestamp = execution.timestamp
            if execution.timestamp > max_timestamp:
                max_timestamp = execution.timestamp

        count = len(executions)

        return QueryStatistics(
            total_count=count,
            algorithms=algorithms,
            statuses=statuses,
            date_range=(min_timestamp, max_timestamp),
            total_execution_time=total_execution_time,
            total_cost=total_cost,
            avg_execution_time=total_execution_time / count,
            avg_cost=total_cost / count if total_cost > 0 else 0.0,
        )

    def get_recent_executions(
        self, hours: int = 24, algorithm: Optional[str] = None, limit: int = 100
    ) -> List[AnalysisExecution]:
        """
        Get recent executions within time window.

        Args:
            hours: Number of hours to look back
            algorithm: Optional algorithm filter
            limit: Max results

        Returns:
            List of recent executions

        Example:
            >>> # Get PageRank executions from last 6 hours
            >>> recent = queries.get_recent_executions(
            ...     hours=6,
            ...     algorithm="pagerank"
            ... )
        """
        start_date = datetime.now() - timedelta(hours=hours)

        filter = ExecutionFilter(
            start_date=start_date, algorithm=algorithm if algorithm else None
        )

        return self.storage.query_executions(filter, limit=limit, offset=0)

    def get_failed_executions(
        self, start_date: Optional[datetime] = None, limit: int = 100
    ) -> List[AnalysisExecution]:
        """
        Get failed executions for debugging.

        Args:
            start_date: Optional start date filter
            limit: Max results

        Returns:
            List of failed executions with error messages

        Example:
            >>> failed = queries.get_failed_executions(
            ...     start_date=datetime(2026, 1, 1)
            ... )
            >>> for execution in failed:
            ...     print(f"{execution.algorithm}: {execution.error_message}")
        """
        filter = ExecutionFilter(status=ExecutionStatus.FAILED, start_date=start_date)

        return self.storage.query_executions(filter, limit=limit, offset=0)

    def get_slowest_executions(
        self, algorithm: Optional[str] = None, limit: int = 10
    ) -> List[AnalysisExecution]:
        """
        Get slowest executions for performance analysis.

        Args:
            algorithm: Optional algorithm filter
            limit: Number of slowest to return

        Returns:
            List of slowest executions, sorted by execution time

        Example:
            >>> slowest = queries.get_slowest_executions(
            ...     algorithm="pagerank",
            ...     limit=5
            ... )
        """
        filter = ExecutionFilter(algorithm=algorithm if algorithm else None)

        executions = self.storage.query_executions(filter, limit=1000, offset=0)

        # Sort by execution time descending
        executions.sort(
            key=lambda x: x.performance_metrics.execution_time_seconds, reverse=True
        )

        return executions[:limit]

    def get_most_expensive_executions(
        self, algorithm: Optional[str] = None, limit: int = 10
    ) -> List[AnalysisExecution]:
        """
        Get most expensive executions for cost analysis.

        Args:
            algorithm: Optional algorithm filter
            limit: Number to return

        Returns:
            List of most expensive executions

        Example:
            >>> expensive = queries.get_most_expensive_executions(limit=5)
            >>> total_cost = sum(e.performance_metrics.cost_usd for e in expensive)
        """
        filter = ExecutionFilter(algorithm=algorithm if algorithm else None)

        executions = self.storage.query_executions(filter, limit=1000, offset=0)

        # Filter out executions without cost data
        executions_with_cost = [
            e for e in executions if e.performance_metrics.cost_usd is not None
        ]

        # Sort by cost descending
        executions_with_cost.sort(
            key=lambda x: x.performance_metrics.cost_usd or 0.0, reverse=True
        )

        return executions_with_cost[:limit]

    def compare_algorithm_performance(
        self, algorithm: str, start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Compare performance of an algorithm over time.

        Args:
            algorithm: Algorithm to analyze
            start_date: Optional start date

        Returns:
            Dictionary with performance metrics

        Example:
            >>> perf = queries.compare_algorithm_performance("pagerank")
            >>> print(f"Avg: {perf['avg_time']}s, Max: {perf['max_time']}s")
        """
        filter = ExecutionFilter(algorithm=algorithm, start_date=start_date)

        executions = self.storage.query_executions(filter, limit=10000, offset=0)

        if not executions:
            return {
                "algorithm": algorithm,
                "count": 0,
                "avg_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "total_cost": 0.0,
            }

        times = [e.performance_metrics.execution_time_seconds for e in executions]
        costs = [
            e.performance_metrics.cost_usd
            for e in executions
            if e.performance_metrics.cost_usd is not None
        ]

        return {
            "algorithm": algorithm,
            "count": len(executions),
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_cost": sum(costs) if costs else 0.0,
            "avg_cost": sum(costs) / len(costs) if costs else 0.0,
            "date_range": (executions[-1].timestamp, executions[0].timestamp),
        }

    def _get_sort_key(self, execution: AnalysisExecution, field: str) -> Any:
        """Get sort key for an execution."""
        if field == "timestamp":
            return execution.timestamp
        elif field == "execution_time":
            return execution.performance_metrics.execution_time_seconds
        elif field == "cost":
            return execution.performance_metrics.cost_usd or 0.0
        elif field == "algorithm":
            return execution.algorithm
        elif field == "result_count":
            return execution.result_count
        else:
            # Try to get from metadata
            return execution.metadata.get(field, "")
