"""
Data models for the Analysis Catalog system.

These models define the structure of catalog entities including executions,
epochs, requirements, use cases, and templates.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any


class ExecutionStatus(Enum):
    """Status of an analysis execution."""

    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    RUNNING = "running"


class EpochStatus(Enum):
    """Status of an analysis epoch."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class GraphConfig:
    """
    Graph configuration for an analysis.

    Captures which graph and collections were analyzed.
    """

    graph_name: str
    """Name of the graph analyzed."""

    graph_type: str
    """Type: 'named_graph' or 'explicit_collections'."""

    vertex_collections: List[str]
    """List of vertex collections used."""

    edge_collections: List[str]
    """List of edge collections used."""

    vertex_count: int
    """Total number of vertices at execution time."""

    edge_count: int
    """Total number of edges at execution time."""

    graph_snapshot_hash: Optional[str] = None
    """Optional hash of graph structure for change detection."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "graph_name": self.graph_name,
            "graph_type": self.graph_type,
            "vertex_collections": self.vertex_collections,
            "edge_collections": self.edge_collections,
            "vertex_count": self.vertex_count,
            "edge_count": self.edge_count,
            "graph_snapshot_hash": self.graph_snapshot_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphConfig":
        """Create from dictionary."""
        return cls(
            graph_name=data["graph_name"],
            graph_type=data["graph_type"],
            vertex_collections=data["vertex_collections"],
            edge_collections=data["edge_collections"],
            vertex_count=data["vertex_count"],
            edge_count=data["edge_count"],
            graph_snapshot_hash=data.get("graph_snapshot_hash"),
        )


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for an execution.

    Tracks resource usage, timing, and costs.
    """

    execution_time_seconds: float
    """Total execution time in seconds."""

    memory_usage_mb: Optional[float] = None
    """Average memory usage in MB."""

    memory_peak_mb: Optional[float] = None
    """Peak memory usage in MB."""

    cpu_time_seconds: Optional[float] = None
    """CPU time in seconds."""

    io_operations: Optional[int] = None
    """Number of I/O operations."""

    network_bytes_sent: Optional[int] = None
    """Bytes sent over network."""

    network_bytes_received: Optional[int] = None
    """Bytes received over network."""

    cost_usd: Optional[float] = None
    """Estimated cost in USD."""

    engine_size: Optional[str] = None
    """Engine size used (e.g., 'e16', 'e32')."""

    cluster_nodes: Optional[int] = None
    """Number of cluster nodes."""

    parallel_workers: Optional[int] = None
    """Number of parallel workers."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_time_seconds": self.execution_time_seconds,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_peak_mb": self.memory_peak_mb,
            "cpu_time_seconds": self.cpu_time_seconds,
            "io_operations": self.io_operations,
            "network_bytes_sent": self.network_bytes_sent,
            "network_bytes_received": self.network_bytes_received,
            "cost_usd": self.cost_usd,
            "engine_size": self.engine_size,
            "cluster_nodes": self.cluster_nodes,
            "parallel_workers": self.parallel_workers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceMetrics":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ResultSample:
    """
    Sample of analysis results for fast queries.

    Stores top N results and summary statistics to enable
    fast time-series queries without scanning full result collections.
    """

    top_results: List[Dict[str, Any]]
    """Top N results (e.g., top 100 by score)."""

    summary_stats: Dict[str, float]
    """Summary statistics (mean, median, std_dev, etc.)."""

    distribution_histogram: Optional[Dict[str, List]] = None
    """Optional histogram of result distribution."""

    sample_size: int = 100
    """Number of top results sampled."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "top_results": self.top_results,
            "summary_stats": self.summary_stats,
            "distribution_histogram": self.distribution_histogram,
            "sample_size": self.sample_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResultSample":
        """Create from dictionary."""
        return cls(
            top_results=data["top_results"],
            summary_stats=data["summary_stats"],
            distribution_histogram=data.get("distribution_histogram"),
            sample_size=data.get("sample_size", 100),
        )


@dataclass
class AnalysisExecution:
    """
    Record of a single analysis execution.

    This is the core entity in the catalog, tracking every analysis
    that runs through the system.
    """

    execution_id: str
    """Unique identifier for this execution."""

    timestamp: datetime
    """When the execution started."""

    algorithm: str
    """Algorithm name (e.g., 'pagerank', 'wcc')."""

    algorithm_version: str
    """Algorithm version."""

    parameters: Dict[str, Any]
    """Algorithm parameters."""

    template_id: str
    """Template ID used."""

    template_name: str
    """Human-readable template name."""

    graph_config: GraphConfig
    """Graph configuration at execution time."""

    results_location: str
    """Collection where results are stored."""

    result_count: int
    """Number of result documents."""

    performance_metrics: PerformanceMetrics
    """Performance and resource metrics."""

    status: ExecutionStatus
    """Execution status."""

    # Lineage fields
    requirements_id: Optional[str] = None
    """ID of source requirements (for agentic workflows)."""

    use_case_id: Optional[str] = None
    """ID of source use case (for agentic workflows)."""

    # Organizational fields
    epoch_id: Optional[str] = None
    """Epoch this execution belongs to."""

    # Sampling for fast queries
    result_sample: Optional[ResultSample] = None
    """Sample of results for fast time-series queries."""

    # Error tracking
    error_message: Optional[str] = None
    """Error message if execution failed."""

    # Metadata
    workflow_mode: Optional[str] = None
    """Workflow mode used: 'traditional', 'agentic', 'parallel_agentic'."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional custom metadata."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "_key": self.execution_id,  # ArangoDB key
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "algorithm": self.algorithm,
            "algorithm_version": self.algorithm_version,
            "parameters": self.parameters,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "graph_config": self.graph_config.to_dict(),
            "results_location": self.results_location,
            "result_count": self.result_count,
            "performance_metrics": self.performance_metrics.to_dict(),
            "status": self.status.value,
            "requirements_id": self.requirements_id,
            "use_case_id": self.use_case_id,
            "epoch_id": self.epoch_id,
            "result_sample": (
                self.result_sample.to_dict() if self.result_sample else None
            ),
            "error_message": self.error_message,
            "workflow_mode": self.workflow_mode,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisExecution":
        """Create from dictionary."""
        return cls(
            execution_id=data["execution_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            algorithm=data["algorithm"],
            algorithm_version=data["algorithm_version"],
            parameters=data["parameters"],
            template_id=data["template_id"],
            template_name=data["template_name"],
            graph_config=GraphConfig.from_dict(data["graph_config"]),
            results_location=data["results_location"],
            result_count=data["result_count"],
            performance_metrics=PerformanceMetrics.from_dict(
                data["performance_metrics"]
            ),
            status=ExecutionStatus(data["status"]),
            requirements_id=data.get("requirements_id"),
            use_case_id=data.get("use_case_id"),
            epoch_id=data.get("epoch_id"),
            result_sample=(
                ResultSample.from_dict(data["result_sample"])
                if data.get("result_sample")
                else None
            ),
            error_message=data.get("error_message"),
            workflow_mode=data.get("workflow_mode"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AnalysisEpoch:
    """
    Group of related analyses run at a specific time.

    Epochs enable time-series analysis by grouping analyses
    into logical snapshots (e.g., "2026-01-snapshot", "daily-2026-01-15").
    """

    epoch_id: str
    """Unique identifier for this epoch."""

    name: str
    """Human-readable epoch name (must be unique)."""

    description: str
    """Description of this epoch."""

    timestamp: datetime
    """Epoch timestamp (when it represents)."""

    created_at: datetime
    """When this epoch record was created."""

    status: EpochStatus
    """Epoch status."""

    tags: List[str]
    """Tags for categorization (e.g., ['production', 'monthly'])."""

    metadata: Dict[str, Any]
    """Additional custom metadata."""

    parent_epoch_id: Optional[str] = None
    """Optional parent epoch for hierarchical organization."""

    analysis_count: int = 0
    """Number of analyses in this epoch (cached)."""

    execution_ids: List[str] = field(default_factory=list)
    """List of execution IDs in this epoch (cached)."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "_key": self.epoch_id,  # ArangoDB key
            "epoch_id": self.epoch_id,
            "name": self.name,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "parent_epoch_id": self.parent_epoch_id,
            "analysis_count": self.analysis_count,
            "execution_ids": self.execution_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisEpoch":
        """Create from dictionary."""
        return cls(
            epoch_id=data["epoch_id"],
            name=data["name"],
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            status=EpochStatus(data["status"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            parent_epoch_id=data.get("parent_epoch_id"),
            analysis_count=data.get("analysis_count", 0),
            execution_ids=data.get("execution_ids", []),
        )


@dataclass
class ExtractedRequirements:
    """
    Extracted requirements from agentic workflow.

    Tracks requirements extracted by the RequirementsAgent.
    """

    requirements_id: str
    """Unique identifier."""

    timestamp: datetime
    """When requirements were extracted."""

    source_documents: List[str]
    """Source document paths."""

    domain: str
    """Domain (e.g., 'e-commerce', 'social-network')."""

    summary: str
    """Brief summary of requirements."""

    objectives: List[Dict[str, Any]]
    """List of business objectives."""

    requirements: List[Dict[str, Any]]
    """List of specific requirements."""

    constraints: List[str]
    """List of constraints."""

    epoch_id: Optional[str] = None
    """Associated epoch."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "_key": self.requirements_id,
            "requirements_id": self.requirements_id,
            "timestamp": self.timestamp.isoformat(),
            "source_documents": self.source_documents,
            "domain": self.domain,
            "summary": self.summary,
            "objectives": self.objectives,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "epoch_id": self.epoch_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractedRequirements":
        """Create from dictionary."""
        return cls(
            requirements_id=data["requirements_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source_documents=data["source_documents"],
            domain=data["domain"],
            summary=data["summary"],
            objectives=data["objectives"],
            requirements=data["requirements"],
            constraints=data["constraints"],
            epoch_id=data.get("epoch_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class GeneratedUseCase:
    """
    Generated use case from agentic workflow.

    Tracks use cases generated by the UseCaseAgent.
    """

    use_case_id: str
    requirements_id: str
    timestamp: datetime
    title: str
    description: str
    algorithm: str
    business_value: str
    priority: str
    addresses_objectives: List[str]
    addresses_requirements: List[str]
    epoch_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "_key": self.use_case_id,
            "use_case_id": self.use_case_id,
            "requirements_id": self.requirements_id,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "description": self.description,
            "algorithm": self.algorithm,
            "business_value": self.business_value,
            "priority": self.priority,
            "addresses_objectives": self.addresses_objectives,
            "addresses_requirements": self.addresses_requirements,
            "epoch_id": self.epoch_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratedUseCase":
        """Create from dictionary."""
        return cls(
            use_case_id=data["use_case_id"],
            requirements_id=data["requirements_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            title=data["title"],
            description=data["description"],
            algorithm=data["algorithm"],
            business_value=data["business_value"],
            priority=data["priority"],
            addresses_objectives=data["addresses_objectives"],
            addresses_requirements=data["addresses_requirements"],
            epoch_id=data.get("epoch_id"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AnalysisTemplate:
    """
    Analysis template record.

    Tracks templates generated by the TemplateAgent.
    """

    template_id: str
    use_case_id: str
    requirements_id: str
    timestamp: datetime
    name: str
    algorithm: str
    parameters: Dict[str, Any]
    graph_config: GraphConfig
    epoch_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "_key": self.template_id,
            "template_id": self.template_id,
            "use_case_id": self.use_case_id,
            "requirements_id": self.requirements_id,
            "timestamp": self.timestamp.isoformat(),
            "name": self.name,
            "algorithm": self.algorithm,
            "parameters": self.parameters,
            "graph_config": self.graph_config.to_dict(),
            "epoch_id": self.epoch_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisTemplate":
        """Create from dictionary."""
        return cls(
            template_id=data["template_id"],
            use_case_id=data["use_case_id"],
            requirements_id=data["requirements_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            name=data["name"],
            algorithm=data["algorithm"],
            parameters=data["parameters"],
            graph_config=GraphConfig.from_dict(data["graph_config"]),
            epoch_id=data.get("epoch_id"),
            metadata=data.get("metadata", {}),
        )


# Filter models


@dataclass
class ExecutionFilter:
    """Filter criteria for querying executions."""

    epoch_id: Optional[str] = None
    algorithm: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    graph_name: Optional[str] = None
    requirements_id: Optional[str] = None
    use_case_id: Optional[str] = None
    workflow_mode: Optional[str] = None
    tags: Optional[List[str]] = None
    min_result_count: Optional[int] = None
    max_execution_time: Optional[float] = None


@dataclass
class EpochFilter:
    """Filter criteria for querying epochs."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    status: Optional[EpochStatus] = None
    name_pattern: Optional[str] = None


# Lineage models


@dataclass
class ExecutionLineage:
    """Complete lineage from requirements to execution."""

    execution: AnalysisExecution
    template: Optional[AnalysisTemplate]
    use_case: Optional[GeneratedUseCase]
    requirements: Optional[ExtractedRequirements]
    epoch: Optional[AnalysisEpoch]


@dataclass
class RequirementTrace:
    """Trace of a specific requirement through pipeline."""

    requirement_id: str
    requirements: ExtractedRequirements
    use_cases: List[GeneratedUseCase]
    templates: List[AnalysisTemplate]
    executions: List[AnalysisExecution]


# Statistics models


@dataclass
class CatalogStatistics:
    """Statistics about the catalog."""

    total_executions: int
    total_epochs: int
    earliest_execution: Optional[datetime]
    latest_execution: Optional[datetime]
    algorithms_used: List[str]
    execution_count_by_algorithm: Dict[str, int]
    execution_count_by_status: Dict[str, int]
    total_execution_time_hours: float
    total_cost_usd: float


# Utility functions


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    return str(uuid.uuid4())


def generate_epoch_id() -> str:
    """Generate a unique epoch ID."""
    return str(uuid.uuid4())


def generate_requirements_id() -> str:
    """Generate a unique requirements ID."""
    return str(uuid.uuid4())


def generate_use_case_id() -> str:
    """Generate a unique use case ID."""
    return str(uuid.uuid4())


def generate_template_id() -> str:
    """Generate a unique template ID."""
    return str(uuid.uuid4())


def current_timestamp() -> datetime:
    """Get current timestamp in UTC."""
    return datetime.now(timezone.utc)
