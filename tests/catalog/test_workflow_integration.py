"""
Tests for catalog integration with workflows.

Tests automatic tracking in traditional, agentic, and parallel workflows.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from graph_analytics_ai.ai.execution.executor import AnalysisExecutor
from graph_analytics_ai.ai.execution.models import ExecutionConfig
from graph_analytics_ai.ai.templates.models import AnalysisTemplate
from graph_analytics_ai.catalog import AnalysisCatalog


@pytest.fixture
def mock_catalog():
    """Create mock catalog."""
    catalog = Mock(spec=AnalysisCatalog)
    catalog.track_execution = Mock(return_value="exec-123")
    return catalog


@pytest.fixture
def mock_orchestrator():
    """Create mock orchestrator."""
    orchestrator = Mock()
    # Mock successful analysis result
    from graph_analytics_ai.gae_orchestrator import (
        AnalysisResult,
        AnalysisStatus,
        AnalysisConfig,
    )

    # Create dummy config
    config = AnalysisConfig(
        name="test",
        algorithm="pagerank",
        vertex_collections=["users"],
        edge_collections=["follows"],
    )

    result = AnalysisResult(
        config=config,
        status=AnalysisStatus.COMPLETED,
        start_time=datetime.now(),
        job_id="job-123",
        documents_updated=100,
        duration_seconds=10.5,
    )
    orchestrator.run_analysis = Mock(return_value=result)
    return orchestrator


@pytest.fixture
def sample_template():
    """Create sample template."""
    from graph_analytics_ai.ai.templates.models import (
        AlgorithmParameters,
        TemplateConfig,
        AlgorithmType,
        EngineSize,
    )

    algo_params = AlgorithmParameters(
        algorithm=AlgorithmType.PAGERANK,
        parameters={"damping": 0.85, "max_iterations": 100},
    )

    config = TemplateConfig(
        graph_name="social_network",
        vertex_collections=["users"],
        edge_collections=["follows"],
        engine_size=EngineSize.SMALL,
        result_collection="test_results",
    )

    from graph_analytics_ai.ai.templates.models import AnalysisTemplate

    template = AnalysisTemplate(
        name="PageRank Test",
        description="Test template",
        use_case_id="uc-123",
        algorithm=algo_params,
        config=config,
        estimated_runtime_seconds=10.0,
    )

    # Add required attributes for tracking
    template.template_id = "template-123"

    return template


class TestCatalogIntegration:
    """Test catalog integration with executor."""

    def test_executor_without_catalog(self, mock_orchestrator, sample_template):
        """Test executor works without catalog (backward compatibility)."""
        executor = AnalysisExecutor(orchestrator=mock_orchestrator)

        # Should work fine without catalog
        result = executor.execute_template(sample_template)

        assert result.success
        assert executor.catalog is None
        assert not executor.auto_track

    def test_executor_with_catalog_disabled(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test executor with catalog but tracking disabled."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator, catalog=mock_catalog, auto_track=False
        )

        result = executor.execute_template(sample_template)

        assert result.success
        # Catalog should not be called
        mock_catalog.track_execution.assert_not_called()

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_executor_tracks_execution(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test executor automatically tracks executions."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator,
            catalog=mock_catalog,
            auto_track=True,
            epoch_id="epoch-123",
            workflow_mode="traditional",
        )

        result = executor.execute_template(sample_template)

        assert result.success

        # Verify catalog was called
        mock_catalog.track_execution.assert_called_once()

        # Verify execution record
        call_args = mock_catalog.track_execution.call_args
        execution = call_args[0][0]

        assert execution.algorithm == "pagerank"
        assert execution.template_name == "PageRank Test"
        assert execution.epoch_id == "epoch-123"
        assert execution.workflow_mode == "traditional"
        assert execution.use_case_id == "uc-123"

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_executor_tracks_with_lineage(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test executor tracks with lineage information."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator, catalog=mock_catalog, auto_track=True
        )

        result = executor.execute_template(
            sample_template,
            epoch_id="epoch-456",
            requirements_id="req-789",
            use_case_id="uc-override",
        )

        assert result.success

        # Verify lineage was passed
        execution = mock_catalog.track_execution.call_args[0][0]
        assert execution.requirements_id == "req-789"
        assert execution.use_case_id == "uc-override"
        assert execution.epoch_id == "epoch-456"

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_tracking_failure_doesnt_break_execution(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test that catalog tracking failures don't break execution."""
        # Make catalog raise an error
        mock_catalog.track_execution.side_effect = Exception("Catalog error")

        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator, catalog=mock_catalog, auto_track=True
        )

        # Execution should still succeed
        result = executor.execute_template(sample_template)

        assert result.success
        mock_catalog.track_execution.assert_called_once()

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_batch_execution_tracks_all(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test batch execution tracks all templates."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator, catalog=mock_catalog, auto_track=True
        )

        # Execute batch of 3 templates
        templates = [sample_template, sample_template, sample_template]

        results = executor.execute_batch(templates)

        assert len(results) == 3
        assert all(r.success for r in results)

        # Should track all 3
        assert mock_catalog.track_execution.call_count == 3

    def test_executor_with_custom_workflow_mode(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test executor with custom workflow mode."""
        with patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True):
            executor = AnalysisExecutor(
                orchestrator=mock_orchestrator,
                catalog=mock_catalog,
                auto_track=True,
                workflow_mode="custom_workflow",
            )

            result = executor.execute_template(sample_template)

            assert result.success

            execution = mock_catalog.track_execution.call_args[0][0]
            assert execution.workflow_mode == "custom_workflow"


class TestWorkflowModes:
    """Test tracking with different workflow modes."""

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_traditional_workflow_mode(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test traditional workflow mode tracking."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator,
            catalog=mock_catalog,
            workflow_mode="traditional",
        )

        executor.execute_template(sample_template)

        execution = mock_catalog.track_execution.call_args[0][0]
        assert execution.workflow_mode == "traditional"

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_agentic_workflow_mode(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test agentic workflow mode tracking."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator,
            catalog=mock_catalog,
            workflow_mode="agentic",
        )

        executor.execute_template(
            sample_template, requirements_id="req-123", use_case_id="uc-456"
        )

        execution = mock_catalog.track_execution.call_args[0][0]
        assert execution.workflow_mode == "agentic"
        assert execution.requirements_id == "req-123"
        assert execution.use_case_id == "uc-456"

    @patch("graph_analytics_ai.ai.execution.executor.CATALOG_AVAILABLE", True)
    def test_parallel_agentic_workflow_mode(
        self, mock_catalog, mock_orchestrator, sample_template
    ):
        """Test parallel agentic workflow mode tracking."""
        executor = AnalysisExecutor(
            orchestrator=mock_orchestrator,
            catalog=mock_catalog,
            workflow_mode="parallel_agentic",
        )

        executor.execute_template(sample_template)

        execution = mock_catalog.track_execution.call_args[0][0]
        assert execution.workflow_mode == "parallel_agentic"
