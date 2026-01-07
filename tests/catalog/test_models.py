"""
Unit tests for catalog data models.

Tests serialization, validation, and model methods.
"""

from datetime import datetime, timezone

from graph_analytics_ai.catalog.models import (
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
    generate_execution_id,
    generate_epoch_id,
    current_timestamp,
)


class TestGraphConfig:
    """Test GraphConfig model."""

    def test_to_dict_from_dict(self):
        """Test serialization round trip."""
        config = GraphConfig(
            graph_name="test_graph",
            graph_type="named_graph",
            vertex_collections=["users", "products"],
            edge_collections=["purchases"],
            vertex_count=1000,
            edge_count=5000,
            graph_snapshot_hash="abc123",
        )

        # Convert to dict and back
        dict_data = config.to_dict()
        restored = GraphConfig.from_dict(dict_data)

        assert restored.graph_name == config.graph_name
        assert restored.vertex_count == config.vertex_count
        assert restored.graph_snapshot_hash == config.graph_snapshot_hash


class TestPerformanceMetrics:
    """Test PerformanceMetrics model."""

    def test_to_dict_from_dict(self):
        """Test serialization with all fields."""
        metrics = PerformanceMetrics(
            execution_time_seconds=45.5,
            memory_usage_mb=512.0,
            memory_peak_mb=1024.0,
            cpu_time_seconds=40.0,
            cost_usd=1.25,
            engine_size="e16",
        )

        dict_data = metrics.to_dict()
        restored = PerformanceMetrics.from_dict(dict_data)

        assert restored.execution_time_seconds == 45.5
        assert restored.cost_usd == 1.25

    def test_optional_fields(self):
        """Test that optional fields work."""
        metrics = PerformanceMetrics(execution_time_seconds=10.0)

        assert metrics.memory_usage_mb is None
        assert metrics.cost_usd is None


class TestResultSample:
    """Test ResultSample model."""

    def test_to_dict_from_dict(self):
        """Test serialization."""
        sample = ResultSample(
            top_results=[
                {"_key": "user1", "score": 0.95},
                {"_key": "user2", "score": 0.85},
            ],
            summary_stats={
                "mean": 0.5,
                "median": 0.48,
                "std_dev": 0.15,
            },
            sample_size=100,
        )

        dict_data = sample.to_dict()
        restored = ResultSample.from_dict(dict_data)

        assert len(restored.top_results) == 2
        assert restored.summary_stats["mean"] == 0.5
        assert restored.sample_size == 100


class TestAnalysisExecution:
    """Test AnalysisExecution model."""

    def test_complete_execution(self):
        """Test execution with all fields."""
        timestamp = datetime.now(timezone.utc)

        execution = AnalysisExecution(
            execution_id="exec-123",
            timestamp=timestamp,
            algorithm="pagerank",
            algorithm_version="1.0",
            parameters={"damping": 0.85, "max_iterations": 100},
            template_id="template-1",
            template_name="PageRank Analysis",
            graph_config=GraphConfig(
                graph_name="social",
                graph_type="named_graph",
                vertex_collections=["users"],
                edge_collections=["follows"],
                vertex_count=1000,
                edge_count=5000,
            ),
            results_location="pagerank_results",
            result_count=1000,
            performance_metrics=PerformanceMetrics(
                execution_time_seconds=45.5,
                cost_usd=1.25,
            ),
            status=ExecutionStatus.COMPLETED,
            epoch_id="epoch-1",
            workflow_mode="parallel_agentic",
        )

        # Test serialization
        dict_data = execution.to_dict()
        assert dict_data["_key"] == "exec-123"
        assert dict_data["algorithm"] == "pagerank"
        assert dict_data["status"] == "completed"

        # Test deserialization
        restored = AnalysisExecution.from_dict(dict_data)
        assert restored.execution_id == execution.execution_id
        assert restored.algorithm == execution.algorithm
        assert restored.status == ExecutionStatus.COMPLETED
        assert restored.workflow_mode == "parallel_agentic"

    def test_minimal_execution(self):
        """Test execution with minimal required fields."""
        timestamp = datetime.now(timezone.utc)

        execution = AnalysisExecution(
            execution_id="exec-min",
            timestamp=timestamp,
            algorithm="wcc",
            algorithm_version="1.0",
            parameters={},
            template_id="template-1",
            template_name="WCC",
            graph_config=GraphConfig(
                graph_name="test",
                graph_type="named_graph",
                vertex_collections=["v"],
                edge_collections=["e"],
                vertex_count=10,
                edge_count=20,
            ),
            results_location="results",
            result_count=10,
            performance_metrics=PerformanceMetrics(execution_time_seconds=1.0),
            status=ExecutionStatus.COMPLETED,
        )

        dict_data = execution.to_dict()
        restored = AnalysisExecution.from_dict(dict_data)

        assert restored.execution_id == "exec-min"
        assert restored.requirements_id is None
        assert restored.epoch_id is None


class TestAnalysisEpoch:
    """Test AnalysisEpoch model."""

    def test_epoch_serialization(self):
        """Test epoch serialization."""
        timestamp = datetime.now(timezone.utc)

        epoch = AnalysisEpoch(
            epoch_id="epoch-123",
            name="2026-01-baseline",
            description="January baseline",
            timestamp=timestamp,
            created_at=timestamp,
            status=EpochStatus.ACTIVE,
            tags=["production", "monthly"],
            metadata={"analyst": "alice"},
        )

        dict_data = epoch.to_dict()
        restored = AnalysisEpoch.from_dict(dict_data)

        assert restored.epoch_id == "epoch-123"
        assert restored.name == "2026-01-baseline"
        assert restored.status == EpochStatus.ACTIVE
        assert "production" in restored.tags


class TestExtractedRequirements:
    """Test ExtractedRequirements model."""

    def test_requirements_serialization(self):
        """Test requirements serialization."""
        timestamp = datetime.now(timezone.utc)

        requirements = ExtractedRequirements(
            requirements_id="req-123",
            timestamp=timestamp,
            source_documents=["requirements.md"],
            domain="e-commerce",
            summary="Analyze customer behavior",
            objectives=[{"id": "obj1", "description": "Find influencers"}],
            requirements=[{"id": "req1", "description": "Compute PageRank"}],
            constraints=["Must complete in 1 hour"],
            epoch_id="epoch-1",
        )

        dict_data = requirements.to_dict()
        restored = ExtractedRequirements.from_dict(dict_data)

        assert restored.requirements_id == "req-123"
        assert restored.domain == "e-commerce"
        assert len(restored.objectives) == 1


class TestGeneratedUseCase:
    """Test GeneratedUseCase model."""

    def test_use_case_serialization(self):
        """Test use case serialization."""
        timestamp = datetime.now(timezone.utc)

        use_case = GeneratedUseCase(
            use_case_id="uc-123",
            requirements_id="req-123",
            timestamp=timestamp,
            title="Identify Influencers",
            description="Use PageRank to find top influencers",
            algorithm="pagerank",
            business_value="Targeted marketing",
            priority="high",
            addresses_objectives=["obj1"],
            addresses_requirements=["req1"],
        )

        dict_data = use_case.to_dict()
        restored = GeneratedUseCase.from_dict(dict_data)

        assert restored.use_case_id == "uc-123"
        assert restored.algorithm == "pagerank"
        assert restored.priority == "high"


class TestAnalysisTemplate:
    """Test AnalysisTemplate model."""

    def test_template_serialization(self):
        """Test template serialization."""
        timestamp = datetime.now(timezone.utc)

        template = AnalysisTemplate(
            template_id="template-123",
            use_case_id="uc-123",
            requirements_id="req-123",
            timestamp=timestamp,
            name="PageRank - Influencers",
            algorithm="pagerank",
            parameters={"damping": 0.85},
            graph_config=GraphConfig(
                graph_name="social",
                graph_type="named_graph",
                vertex_collections=["users"],
                edge_collections=["follows"],
                vertex_count=1000,
                edge_count=5000,
            ),
        )

        dict_data = template.to_dict()
        restored = AnalysisTemplate.from_dict(dict_data)

        assert restored.template_id == "template-123"
        assert restored.algorithm == "pagerank"


class TestFilters:
    """Test filter models."""

    def test_execution_filter(self):
        """Test ExecutionFilter."""
        filter = ExecutionFilter(
            algorithm="pagerank",
            status=ExecutionStatus.COMPLETED,
            epoch_id="epoch-1",
        )

        assert filter.algorithm == "pagerank"
        assert filter.status == ExecutionStatus.COMPLETED

    def test_epoch_filter(self):
        """Test EpochFilter."""
        filter = EpochFilter(
            tags=["production"],
            status=EpochStatus.ACTIVE,
        )

        assert "production" in filter.tags
        assert filter.status == EpochStatus.ACTIVE


class TestUtilityFunctions:
    """Test utility functions."""

    def test_generate_execution_id(self):
        """Test execution ID generation."""
        id1 = generate_execution_id()
        id2 = generate_execution_id()

        assert id1 != id2
        assert len(id1) > 0

    def test_generate_epoch_id(self):
        """Test epoch ID generation."""
        id1 = generate_epoch_id()
        id2 = generate_epoch_id()

        assert id1 != id2

    def test_current_timestamp(self):
        """Test timestamp generation."""
        ts = current_timestamp()

        assert ts.tzinfo is not None  # Should have timezone
        assert ts.year >= 2026
