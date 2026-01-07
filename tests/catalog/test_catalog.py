"""
Unit tests for AnalysisCatalog class.

These tests use a mock storage backend to test catalog logic
without requiring a real database.
"""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from graph_analytics_ai.catalog import AnalysisCatalog
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
)
from graph_analytics_ai.catalog.exceptions import ValidationError


@pytest.fixture
def mock_storage():
    """Create mock storage backend."""
    return Mock()


@pytest.fixture
def catalog(mock_storage):
    """Create catalog with mock storage."""
    return AnalysisCatalog(mock_storage)


class TestAnalysisCatalog:
    """Test AnalysisCatalog class."""

    def test_initialization(self, mock_storage):
        """Test catalog initialization."""
        catalog = AnalysisCatalog(mock_storage)
        assert catalog.storage == mock_storage

    def test_track_execution(self, catalog, mock_storage):
        """Test tracking execution."""
        execution = self._create_test_execution()

        mock_storage.insert_execution.return_value = execution.execution_id

        # Track execution
        execution_id = catalog.track_execution(execution)

        assert execution_id == execution.execution_id
        mock_storage.insert_execution.assert_called_once_with(execution)

    def test_track_execution_validation(self, catalog):
        """Test that invalid executions are rejected."""
        # Missing execution_id
        execution = self._create_test_execution()
        execution.execution_id = ""

        with pytest.raises(ValidationError):
            catalog.track_execution(execution)

        # Missing algorithm
        execution = self._create_test_execution()
        execution.algorithm = ""

        with pytest.raises(ValidationError):
            catalog.track_execution(execution)

    def test_get_execution(self, catalog, mock_storage):
        """Test getting execution."""
        execution = self._create_test_execution()
        mock_storage.get_execution.return_value = execution

        retrieved = catalog.get_execution(execution.execution_id)

        assert retrieved == execution
        mock_storage.get_execution.assert_called_once_with(execution.execution_id)

    def test_query_executions(self, catalog, mock_storage):
        """Test querying executions."""
        executions = [
            self._create_test_execution(),
            self._create_test_execution(),
        ]
        mock_storage.query_executions.return_value = executions

        filter = ExecutionFilter(algorithm="pagerank")
        result = catalog.query_executions(filter=filter, limit=50)

        assert len(result) == 2
        mock_storage.query_executions.assert_called_once_with(filter, 50, 0)

    def test_delete_execution(self, catalog, mock_storage):
        """Test deleting execution."""
        execution_id = "exec-123"

        catalog.delete_execution(execution_id)

        mock_storage.delete_execution.assert_called_once_with(execution_id)

    def test_create_epoch(self, catalog, mock_storage):
        """Test creating epoch."""
        mock_storage.get_epoch_by_name.return_value = None
        mock_storage.insert_epoch.return_value = "epoch-123"

        epoch = catalog.create_epoch(
            name="test-epoch",
            description="Test",
            tags=["test"],
        )

        assert epoch.name == "test-epoch"
        assert epoch.status == EpochStatus.ACTIVE
        assert "test" in epoch.tags

        # Verify storage was called
        mock_storage.get_epoch_by_name.assert_called_once_with("test-epoch")
        mock_storage.insert_epoch.assert_called_once()

    def test_create_epoch_duplicate_name(self, catalog, mock_storage):
        """Test that duplicate epoch names are rejected."""
        # Simulate existing epoch
        existing_epoch = AnalysisEpoch(
            epoch_id="epoch-1",
            name="existing",
            description="",
            timestamp=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            status=EpochStatus.ACTIVE,
            tags=[],
            metadata={},
        )
        mock_storage.get_epoch_by_name.return_value = existing_epoch

        with pytest.raises(ValidationError, match="already exists"):
            catalog.create_epoch(name="existing")

    def test_create_epoch_empty_name(self, catalog):
        """Test that empty epoch names are rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            catalog.create_epoch(name="")

        with pytest.raises(ValidationError, match="cannot be empty"):
            catalog.create_epoch(name="   ")

    def test_get_epoch(self, catalog, mock_storage):
        """Test getting epoch."""
        epoch = AnalysisEpoch(
            epoch_id="epoch-123",
            name="test",
            description="",
            timestamp=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            status=EpochStatus.ACTIVE,
            tags=[],
            metadata={},
        )
        mock_storage.get_epoch.return_value = epoch

        retrieved = catalog.get_epoch("epoch-123")

        assert retrieved == epoch
        mock_storage.get_epoch.assert_called_once_with("epoch-123")

    def test_delete_epoch(self, catalog, mock_storage):
        """Test deleting epoch."""
        catalog.delete_epoch("epoch-123", cascade=True)

        mock_storage.delete_epoch.assert_called_once_with("epoch-123", True)

    def test_track_requirements(self, catalog, mock_storage):
        """Test tracking requirements."""
        requirements = ExtractedRequirements(
            requirements_id="req-123",
            timestamp=datetime.now(timezone.utc),
            source_documents=["test.md"],
            domain="test",
            summary="Test",
            objectives=[],
            requirements=[],
            constraints=[],
        )

        mock_storage.insert_requirements.return_value = requirements.requirements_id

        req_id = catalog.track_requirements(requirements)

        assert req_id == "req-123"
        mock_storage.insert_requirements.assert_called_once_with(requirements)

    def test_get_execution_lineage(self, catalog, mock_storage):
        """Test getting execution lineage."""
        execution = self._create_test_execution(
            template_id="template-1",
            use_case_id="uc-1",
            requirements_id="req-1",
            epoch_id="epoch-1",
        )

        template = AnalysisTemplate(
            template_id="template-1",
            use_case_id="uc-1",
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            name="Test Template",
            algorithm="pagerank",
            parameters={},
            graph_config=execution.graph_config,
        )

        use_case = GeneratedUseCase(
            use_case_id="uc-1",
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            title="Test",
            description="Test",
            algorithm="pagerank",
            business_value="Test",
            priority="high",
            addresses_objectives=[],
            addresses_requirements=[],
        )

        requirements = ExtractedRequirements(
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            source_documents=["test.md"],
            domain="test",
            summary="Test",
            objectives=[],
            requirements=[],
            constraints=[],
        )

        epoch = AnalysisEpoch(
            epoch_id="epoch-1",
            name="test",
            description="",
            timestamp=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            status=EpochStatus.ACTIVE,
            tags=[],
            metadata={},
        )

        # Mock storage responses
        mock_storage.get_execution.return_value = execution
        mock_storage.get_template.return_value = template
        mock_storage.get_use_case.return_value = use_case
        mock_storage.get_requirements.return_value = requirements
        mock_storage.get_epoch.return_value = epoch

        # Get lineage
        lineage = catalog.get_execution_lineage(execution.execution_id)

        assert lineage.execution == execution
        assert lineage.template == template
        assert lineage.use_case == use_case
        assert lineage.requirements == requirements
        assert lineage.epoch == epoch

    def test_get_execution_lineage_partial(self, catalog, mock_storage):
        """Test lineage with missing optional entities."""
        execution = self._create_test_execution(
            template_id="template-1",
            use_case_id=None,  # No use case
            requirements_id=None,  # No requirements
            epoch_id=None,  # No epoch
        )

        template = AnalysisTemplate(
            template_id="template-1",
            use_case_id="uc-1",
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            name="Test",
            algorithm="pagerank",
            parameters={},
            graph_config=execution.graph_config,
        )

        mock_storage.get_execution.return_value = execution
        mock_storage.get_template.return_value = template
        # get_use_case, get_requirements, get_epoch not called

        lineage = catalog.get_execution_lineage(execution.execution_id)

        assert lineage.execution == execution
        assert lineage.template == template
        assert lineage.use_case is None
        assert lineage.requirements is None
        assert lineage.epoch is None

    def test_trace_requirement(self, catalog, mock_storage):
        """Test tracing requirement through pipeline."""
        requirements = ExtractedRequirements(
            requirements_id="req-1",
            timestamp=datetime.now(timezone.utc),
            source_documents=["test.md"],
            domain="test",
            summary="Test",
            objectives=[],
            requirements=[],
            constraints=[],
        )

        use_cases = [
            GeneratedUseCase(
                use_case_id="uc-1",
                requirements_id="req-1",
                timestamp=datetime.now(timezone.utc),
                title="Test 1",
                description="Test",
                algorithm="pagerank",
                business_value="Test",
                priority="high",
                addresses_objectives=[],
                addresses_requirements=[],
            ),
        ]

        templates = [
            AnalysisTemplate(
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
            ),
        ]

        executions = [self._create_test_execution(requirements_id="req-1")]

        # Mock storage
        mock_storage.get_requirements.return_value = requirements
        mock_storage.query_use_cases_by_requirements.return_value = use_cases
        mock_storage.query_templates_by_use_case.return_value = templates
        mock_storage.query_executions.return_value = executions

        # Trace requirement
        trace = catalog.trace_requirement("req-1")

        assert trace.requirements == requirements
        assert len(trace.use_cases) == 1
        assert len(trace.templates) == 1
        assert len(trace.executions) == 1

    def test_reset(self, catalog, mock_storage):
        """Test resetting catalog."""
        catalog.reset(confirm=True)

        mock_storage.reset.assert_called_once_with(confirm=True)

    def test_export_import(self, catalog, mock_storage):
        """Test export and import."""
        catalog.export_catalog("/tmp/catalog.json")
        mock_storage.export_catalog.assert_called_once_with("/tmp/catalog.json")

        catalog.import_catalog("/tmp/catalog.json")
        mock_storage.import_catalog.assert_called_once_with("/tmp/catalog.json")

    def test_get_statistics(self, catalog, mock_storage):
        """Test getting statistics."""
        mock_storage.get_statistics.return_value = {
            "total_executions": 100,
            "total_epochs": 10,
            "execution_count_by_algorithm": {"pagerank": 50, "wcc": 50},
            "execution_count_by_status": {"completed": 90, "failed": 10},
        }

        stats = catalog.get_statistics()

        assert stats.total_executions == 100
        assert stats.total_epochs == 10
        assert "pagerank" in stats.algorithms_used

    def test_close(self, catalog, mock_storage):
        """Test closing catalog."""
        catalog.close()

        mock_storage.close.assert_called_once()

    # Helper methods

    def _create_test_execution(
        self,
        template_id="template-1",
        use_case_id=None,
        requirements_id=None,
        epoch_id=None,
    ) -> AnalysisExecution:
        """Create test execution."""
        return AnalysisExecution(
            execution_id=generate_execution_id(),
            timestamp=datetime.now(timezone.utc),
            algorithm="pagerank",
            algorithm_version="1.0",
            parameters={"damping": 0.85},
            template_id=template_id,
            template_name="PageRank",
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["users"],
                edge_collections=["follows"],
                vertex_count=100,
                edge_count=500,
            ),
            results_location="results",
            result_count=100,
            performance_metrics=PerformanceMetrics(execution_time_seconds=10.0),
            status=ExecutionStatus.COMPLETED,
            use_case_id=use_case_id,
            requirements_id=requirements_id,
            epoch_id=epoch_id,
        )
