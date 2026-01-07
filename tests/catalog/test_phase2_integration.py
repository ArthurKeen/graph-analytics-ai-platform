"""
Integration tests for Phase 2 features.

Tests advanced queries, lineage tracking, and management operations.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from graph_analytics_ai.catalog import (
    AnalysisCatalog,
    CatalogQueries,
    LineageTracker,
    CatalogManager,
)
from graph_analytics_ai.catalog.models import (
    AnalysisExecution,
    AnalysisEpoch,
    ExtractedRequirements,
    GeneratedUseCase,
    AnalysisTemplate,
    GraphConfig,
    PerformanceMetrics,
    ExecutionStatus,
    EpochStatus,
    ExecutionFilter,
    generate_execution_id,
    generate_epoch_id,
)
from graph_analytics_ai.catalog.queries import SortOption
from graph_analytics_ai.catalog.exceptions import LineageError, ValidationError


@pytest.fixture
def mock_storage():
    """Create mock storage backend."""
    return Mock()


@pytest.fixture
def catalog_queries(mock_storage):
    """Create CatalogQueries instance."""
    return CatalogQueries(mock_storage)


@pytest.fixture
def lineage_tracker(mock_storage):
    """Create LineageTracker instance."""
    return LineageTracker(mock_storage)


@pytest.fixture
def catalog_manager(mock_storage):
    """Create CatalogManager instance."""
    return CatalogManager(mock_storage)


class TestCatalogQueries:
    """Test advanced query operations."""

    def test_query_with_pagination(self, catalog_queries, mock_storage):
        """Test paginated queries."""
        # Create test executions
        executions = [self._create_execution(algorithm=f"algo-{i}") for i in range(25)]
        mock_storage.query_executions.return_value = executions

        # Query first page
        result = catalog_queries.query_with_pagination(
            filter=None, page=1, page_size=10
        )

        assert result.page == 1
        assert result.page_size == 10
        assert result.total_count == 25
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_previous is False
        assert len(result.items) == 10

    def test_query_with_pagination_last_page(self, catalog_queries, mock_storage):
        """Test last page of pagination."""
        executions = [self._create_execution() for i in range(25)]
        mock_storage.query_executions.return_value = executions

        # Query last page
        result = catalog_queries.query_with_pagination(
            filter=None, page=3, page_size=10
        )

        assert result.page == 3
        assert len(result.items) == 5  # Only 5 items on last page
        assert result.has_next is False
        assert result.has_previous is True

    def test_query_with_sorting(self, catalog_queries, mock_storage):
        """Test sorting in queries."""
        executions = [
            self._create_execution(exec_time=10.0),
            self._create_execution(exec_time=5.0),
            self._create_execution(exec_time=15.0),
        ]
        mock_storage.query_executions.return_value = executions

        # Sort by execution time ascending
        result = catalog_queries.query_with_pagination(
            sort=SortOption(field="execution_time", ascending=True),
            page=1,
            page_size=10,
        )

        # Verify sorted order
        times = [e.performance_metrics.execution_time_seconds for e in result.items]
        assert times == sorted(times)

    def test_get_statistics(self, catalog_queries, mock_storage):
        """Test statistics generation."""
        executions = [
            self._create_execution(algorithm="pagerank", exec_time=10.0, cost=1.0),
            self._create_execution(algorithm="pagerank", exec_time=12.0, cost=1.2),
            self._create_execution(algorithm="wcc", exec_time=8.0, cost=0.8),
        ]
        mock_storage.query_executions.return_value = executions

        stats = catalog_queries.get_statistics()

        assert stats.total_count == 3
        assert stats.algorithms["pagerank"] == 2
        assert stats.algorithms["wcc"] == 1
        assert stats.avg_execution_time == 10.0
        assert stats.avg_cost == 1.0

    def test_get_recent_executions(self, catalog_queries, mock_storage):
        """Test recent executions query."""
        now = datetime.now(timezone.utc)
        executions = [
            self._create_execution(timestamp=now - timedelta(hours=1)),
            self._create_execution(timestamp=now - timedelta(hours=2)),
        ]
        mock_storage.query_executions.return_value = executions

        result = catalog_queries.get_recent_executions(hours=6)

        assert len(result) == 2
        # Verify filter was passed to storage
        mock_storage.query_executions.assert_called_once()

    def test_get_failed_executions(self, catalog_queries, mock_storage):
        """Test failed executions query."""
        executions = [
            self._create_execution(status=ExecutionStatus.FAILED),
            self._create_execution(status=ExecutionStatus.FAILED),
        ]
        mock_storage.query_executions.return_value = executions

        result = catalog_queries.get_failed_executions()

        assert len(result) == 2
        assert all(e.status == ExecutionStatus.FAILED for e in result)

    def test_get_slowest_executions(self, catalog_queries, mock_storage):
        """Test slowest executions query."""
        executions = [
            self._create_execution(exec_time=10.0),
            self._create_execution(exec_time=50.0),
            self._create_execution(exec_time=30.0),
            self._create_execution(exec_time=20.0),
        ]
        mock_storage.query_executions.return_value = executions

        result = catalog_queries.get_slowest_executions(limit=2)

        assert len(result) == 2
        assert result[0].performance_metrics.execution_time_seconds == 50.0
        assert result[1].performance_metrics.execution_time_seconds == 30.0

    def test_compare_algorithm_performance(self, catalog_queries, mock_storage):
        """Test algorithm performance comparison."""
        executions = [
            self._create_execution(algorithm="pagerank", exec_time=10.0, cost=1.0),
            self._create_execution(algorithm="pagerank", exec_time=12.0, cost=1.2),
            self._create_execution(algorithm="pagerank", exec_time=8.0, cost=0.8),
        ]
        mock_storage.query_executions.return_value = executions

        perf = catalog_queries.compare_algorithm_performance("pagerank")

        assert perf["count"] == 3
        assert perf["avg_time"] == 10.0
        assert perf["min_time"] == 8.0
        assert perf["max_time"] == 12.0
        assert perf["avg_cost"] == 1.0

    # Helper methods

    def _create_execution(
        self,
        algorithm="pagerank",
        exec_time=10.0,
        cost=None,
        status=ExecutionStatus.COMPLETED,
        timestamp=None,
    ) -> AnalysisExecution:
        """Create test execution."""
        return AnalysisExecution(
            execution_id=generate_execution_id(),
            timestamp=timestamp or datetime.now(timezone.utc),
            algorithm=algorithm,
            algorithm_version="1.0",
            parameters={},
            template_id="template-1",
            template_name=f"{algorithm} Template",
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=100,
                edge_count=500,
            ),
            results_location="results",
            result_count=100,
            performance_metrics=PerformanceMetrics(
                execution_time_seconds=exec_time, cost_usd=cost
            ),
            status=status,
        )


class TestLineageTracker:
    """Test enhanced lineage tracking."""

    def test_get_complete_lineage(self, lineage_tracker, mock_storage):
        """Test complete lineage retrieval."""
        execution = self._create_execution_with_lineage()
        template = self._create_template()
        use_case = self._create_use_case()
        requirements = self._create_requirements()
        epoch = self._create_epoch()

        mock_storage.get_execution.return_value = execution
        mock_storage.get_template.return_value = template
        mock_storage.get_use_case.return_value = use_case
        mock_storage.get_requirements.return_value = requirements
        mock_storage.get_epoch.return_value = epoch

        lineage = lineage_tracker.get_complete_lineage("exec-123")

        assert lineage.execution == execution
        assert lineage.template == template
        assert lineage.use_case == use_case
        assert lineage.requirements == requirements
        assert lineage.epoch == epoch

    def test_trace_requirement_forward(self, lineage_tracker, mock_storage):
        """Test forward requirement tracing."""
        requirements = self._create_requirements()
        use_cases = [self._create_use_case()]
        templates = [self._create_template()]
        executions = [self._create_execution()]

        mock_storage.get_requirements.return_value = requirements
        mock_storage.query_use_cases_by_requirements.return_value = use_cases
        mock_storage.query_templates_by_use_case.return_value = templates
        mock_storage.query_executions.return_value = executions

        trace = lineage_tracker.trace_requirement_forward("req-123")

        assert trace.requirements == requirements
        assert len(trace.use_cases) == 1
        assert len(trace.templates) == 1
        assert len(trace.executions) == 1

    def test_trace_execution_backward(self, lineage_tracker, mock_storage):
        """Test backward execution tracing."""
        execution = self._create_execution_with_lineage()
        template = self._create_template()
        use_case = self._create_use_case()
        requirements = self._create_requirements()

        mock_storage.get_execution.return_value = execution
        mock_storage.get_template.return_value = template
        mock_storage.get_use_case.return_value = use_case
        mock_storage.get_requirements.return_value = requirements

        result = lineage_tracker.trace_execution_backward("exec-123")

        assert result["execution_id"] == "exec-123"
        assert result["complete"] is True
        assert len(result["path"]) == 4
        assert result["path"][0]["type"] == "requirement"
        assert result["path"][3]["type"] == "execution"

    def test_build_lineage_graph(self, lineage_tracker, mock_storage):
        """Test lineage graph building."""
        executions = [self._create_execution_with_lineage()]
        requirements = [self._create_requirements()]
        use_cases = [self._create_use_case()]
        templates = [self._create_template()]

        mock_storage.query_executions.return_value = executions
        mock_storage.get_requirements.return_value = requirements[0]
        mock_storage.get_use_case.return_value = use_cases[0]
        mock_storage.get_template.return_value = templates[0]

        graph = lineage_tracker.build_lineage_graph()

        assert len(graph.executions) == 1
        assert len(graph.edges) == 3  # req->uc, uc->template, template->exec

    def test_analyze_impact_requirement(self, lineage_tracker, mock_storage):
        """Test impact analysis for requirement change."""
        use_cases = [self._create_use_case()]
        templates = [self._create_template()]
        executions = [self._create_execution()]

        mock_storage.query_use_cases_by_requirements.return_value = use_cases
        mock_storage.query_templates_by_use_case.return_value = templates
        mock_storage.query_executions.return_value = executions

        impact = lineage_tracker.analyze_impact("req-123", "requirement")

        assert impact.source_type == "requirement"
        assert len(impact.affected_use_cases) == 1
        assert len(impact.affected_templates) == 1
        assert len(impact.affected_executions) == 1
        assert impact.total_affected == 3

    # Helper methods

    def _create_execution(self) -> AnalysisExecution:
        """Create test execution."""
        return AnalysisExecution(
            execution_id="exec-123",
            timestamp=datetime.now(timezone.utc),
            algorithm="pagerank",
            algorithm_version="1.0",
            parameters={},
            template_id="template-123",
            template_name="PageRank",
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=100,
                edge_count=500,
            ),
            results_location="results",
            result_count=100,
            performance_metrics=PerformanceMetrics(execution_time_seconds=10.0),
            status=ExecutionStatus.COMPLETED,
        )

    def _create_execution_with_lineage(self) -> AnalysisExecution:
        """Create execution with full lineage."""
        exec = self._create_execution()
        exec.requirements_id = "req-123"
        exec.use_case_id = "uc-123"
        exec.epoch_id = "epoch-123"
        return exec

    def _create_template(self) -> AnalysisTemplate:
        """Create test template."""
        return AnalysisTemplate(
            template_id="template-123",
            use_case_id="uc-123",
            requirements_id="req-123",
            timestamp=datetime.now(timezone.utc),
            name="Test Template",
            algorithm="pagerank",
            parameters={},
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=10,
                edge_count=20,
            ),
        )

    def _create_use_case(self) -> GeneratedUseCase:
        """Create test use case."""
        return GeneratedUseCase(
            use_case_id="uc-123",
            requirements_id="req-123",
            timestamp=datetime.now(timezone.utc),
            title="Test Use Case",
            description="Test",
            algorithm="pagerank",
            business_value="Test",
            priority="high",
            addresses_objectives=[],
            addresses_requirements=[],
        )

    def _create_requirements(self) -> ExtractedRequirements:
        """Create test requirements."""
        return ExtractedRequirements(
            requirements_id="req-123",
            timestamp=datetime.now(timezone.utc),
            source_documents=["test.md"],
            domain="test",
            summary="Test requirements",
            objectives=[],
            requirements=[],
            constraints=[],
        )

    def _create_epoch(self) -> AnalysisEpoch:
        """Create test epoch."""
        return AnalysisEpoch(
            epoch_id="epoch-123",
            name="test-epoch",
            description="Test",
            timestamp=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            status=EpochStatus.ACTIVE,
            tags=[],
            metadata={},
        )


class TestCatalogManager:
    """Test catalog management operations."""

    def test_batch_delete_executions_dry_run(self, catalog_manager, mock_storage):
        """Test batch delete in dry run mode."""
        executions = [self._create_execution() for _ in range(5)]
        mock_storage.query_executions.return_value = executions

        result = catalog_manager.batch_delete_executions(
            filter=ExecutionFilter(), dry_run=True
        )

        assert result["count"] == 5
        assert result["dry_run"] is True
        assert len(result["deleted_ids"]) == 0
        # Verify no deletes called
        mock_storage.delete_execution.assert_not_called()

    def test_batch_delete_executions_actual(self, catalog_manager, mock_storage):
        """Test actual batch delete."""
        executions = [self._create_execution(exec_id=f"exec-{i}") for i in range(3)]
        mock_storage.query_executions.return_value = executions

        result = catalog_manager.batch_delete_executions(
            filter=ExecutionFilter(), dry_run=False
        )

        assert result["count"] == 3
        assert result["dry_run"] is False
        assert len(result["deleted_ids"]) == 3
        assert mock_storage.delete_execution.call_count == 3

    def test_archive_old_epochs(self, catalog_manager, mock_storage):
        """Test epoch archival."""
        epochs = [self._create_epoch() for _ in range(2)]
        mock_storage.query_epochs.return_value = epochs

        result = catalog_manager.archive_old_epochs(older_than_days=90, dry_run=False)

        assert result["count"] == 2
        assert len(result["archived_ids"]) == 2
        assert mock_storage.update_epoch.call_count == 2

    def test_cleanup_failed_executions(self, catalog_manager, mock_storage):
        """Test failed execution cleanup."""
        executions = [
            self._create_execution(status=ExecutionStatus.FAILED) for _ in range(3)
        ]
        mock_storage.query_executions.return_value = executions

        result = catalog_manager.cleanup_failed_executions(
            older_than_days=30, dry_run=False
        )

        assert result["count"] == 3
        assert len(result["deleted_ids"]) == 3

    def test_validate_catalog_integrity(self, catalog_manager, mock_storage):
        """Test catalog integrity validation."""
        executions = [self._create_execution()]
        mock_storage.query_executions.return_value = executions
        mock_storage.get_template.return_value = self._create_template()

        integrity = catalog_manager.validate_catalog_integrity()

        assert integrity["executions_checked"] == 1
        assert integrity["error_count"] == 0
        assert integrity["healthy"] is True

    # Helper methods

    def _create_execution(
        self, exec_id=None, status=ExecutionStatus.COMPLETED
    ) -> AnalysisExecution:
        """Create test execution."""
        return AnalysisExecution(
            execution_id=exec_id or generate_execution_id(),
            timestamp=datetime.now(timezone.utc),
            algorithm="pagerank",
            algorithm_version="1.0",
            parameters={},
            template_id="template-1",
            template_name="PageRank",
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=100,
                edge_count=500,
            ),
            results_location="results",
            result_count=100,
            performance_metrics=PerformanceMetrics(execution_time_seconds=10.0),
            status=status,
        )

    def _create_epoch(self) -> AnalysisEpoch:
        """Create test epoch."""
        return AnalysisEpoch(
            epoch_id=generate_epoch_id(),
            name=f"test-epoch-{generate_epoch_id()[:8]}",
            description="Test",
            timestamp=datetime.now(timezone.utc) - timedelta(days=100),
            created_at=datetime.now(timezone.utc),
            status=EpochStatus.ACTIVE,
            tags=[],
            metadata={},
        )

    def _create_template(self) -> AnalysisTemplate:
        """Create test template."""
        return AnalysisTemplate(
            template_id="template-1",
            use_case_id="uc-1",
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            name="Test",
            algorithm="pagerank",
            parameters={},
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=10,
                edge_count=20,
            ),
        )
