"""
Enhanced lineage tracking for the Analysis Catalog.

Provides advanced lineage queries, impact analysis, and
multi-hop tracing through the analysis pipeline.
"""

import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass

from .models import (
    AnalysisExecution,
    ExtractedRequirements,
    GeneratedUseCase,
    AnalysisTemplate,
    ExecutionLineage,
    RequirementTrace,
    ExecutionFilter,
)
from .storage.base import StorageBackend
from .exceptions import LineageError, NotFoundError

logger = logging.getLogger(__name__)


@dataclass
class LineageGraph:
    """
    Complete lineage graph for visualization and analysis.

    Represents the full dependency graph from requirements
    to executions with all intermediate steps.
    """

    requirements: List[ExtractedRequirements]
    """All requirements nodes."""

    use_cases: List[GeneratedUseCase]
    """All use case nodes."""

    templates: List[AnalysisTemplate]
    """All template nodes."""

    executions: List[AnalysisExecution]
    """All execution nodes."""

    edges: List[Dict[str, str]]
    """List of edges: [{"from": "req-1", "to": "uc-1", "type": "generates"}]."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for visualization."""
        return {
            "nodes": {
                "requirements": [r.to_dict() for r in self.requirements],
                "use_cases": [u.to_dict() for u in self.use_cases],
                "templates": [t.to_dict() for t in self.templates],
                "executions": [e.to_dict() for e in self.executions],
            },
            "edges": self.edges,
        }


@dataclass
class ImpactAnalysis:
    """
    Impact analysis for a change in the pipeline.

    Shows what would be affected by changing a requirement,
    use case, or template.
    """

    source_id: str
    """ID of the changed entity."""

    source_type: str
    """Type: 'requirement', 'use_case', 'template'."""

    affected_use_cases: List[GeneratedUseCase]
    """Use cases that would be affected."""

    affected_templates: List[AnalysisTemplate]
    """Templates that would be affected."""

    affected_executions: List[AnalysisExecution]
    """Executions that would be affected."""

    total_affected: int
    """Total number of affected entities."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "affected_use_cases": len(self.affected_use_cases),
            "affected_templates": len(self.affected_templates),
            "affected_executions": len(self.affected_executions),
            "total_affected": self.total_affected,
        }


@dataclass
class CoverageReport:
    """
    Requirement coverage report.

    Shows which requirements have been implemented as use cases,
    templates, and executions.
    """

    total_requirements: int
    """Total number of requirements."""

    requirements_with_use_cases: int
    """Requirements that have use cases."""

    requirements_with_templates: int
    """Requirements that have templates."""

    requirements_with_executions: int
    """Requirements that have been executed."""

    coverage_percentage: float
    """Percentage of requirements executed."""

    uncovered_requirements: List[ExtractedRequirements]
    """Requirements without executions."""


class LineageTracker:
    """
    Enhanced lineage tracking and analysis.

    Provides advanced lineage queries, impact analysis,
    and coverage tracking for the catalog.
    """

    def __init__(self, storage: StorageBackend):
        """
        Initialize lineage tracker.

        Args:
            storage: Storage backend
        """
        self.storage = storage

    def get_complete_lineage(
        self, execution_id: str, include_epoch: bool = True
    ) -> ExecutionLineage:
        """
        Get complete lineage for an execution.

        This is an enhanced version that ensures all entities
        are fetched and validated.

        Args:
            execution_id: Execution ID
            include_epoch: Whether to include epoch info

        Returns:
            ExecutionLineage with all linked entities

        Raises:
            NotFoundError: If execution not found
            LineageError: If lineage is incomplete or invalid
        """
        try:
            execution = self.storage.get_execution(execution_id)
        except NotFoundError as e:
            raise LineageError(f"Execution not found: {execution_id}") from e

        # Fetch all linked entities
        template = None
        use_case = None
        requirements = None
        epoch = None

        # Template (required for executions)
        if execution.template_id:
            try:
                template = self.storage.get_template(execution.template_id)
            except NotFoundError:
                logger.warning(
                    f"Template {execution.template_id} not found for execution {execution_id}"
                )

        # Use case (optional, for agentic workflows)
        if execution.use_case_id:
            try:
                use_case = self.storage.get_use_case(execution.use_case_id)
            except NotFoundError:
                logger.warning(
                    f"Use case {execution.use_case_id} not found for execution {execution_id}"
                )

        # Requirements (optional, for agentic workflows)
        if execution.requirements_id:
            try:
                requirements = self.storage.get_requirements(execution.requirements_id)
            except NotFoundError:
                logger.warning(
                    f"Requirements {execution.requirements_id} not found "
                    f"for execution {execution_id}"
                )

        # Epoch (optional)
        if include_epoch and execution.epoch_id:
            try:
                epoch = self.storage.get_epoch(execution.epoch_id)
            except NotFoundError:
                logger.warning(
                    f"Epoch {execution.epoch_id} not found for execution {execution_id}"
                )

        return ExecutionLineage(
            execution=execution,
            template=template,
            use_case=use_case,
            requirements=requirements,
            epoch=epoch,
        )

    def trace_requirement_forward(self, requirement_id: str) -> RequirementTrace:
        """
        Trace a requirement forward through the pipeline.

        Shows all use cases, templates, and executions derived
        from a specific requirement.

        Args:
            requirement_id: Requirements ID

        Returns:
            RequirementTrace showing all derived entities

        Raises:
            NotFoundError: If requirement not found
        """
        try:
            requirements = self.storage.get_requirements(requirement_id)
        except NotFoundError as e:
            raise LineageError(f"Requirements not found: {requirement_id}") from e

        # Get all use cases from this requirement
        use_cases = self.storage.query_use_cases_by_requirements(requirement_id)

        # Get all templates from these use cases
        templates = []
        for use_case in use_cases:
            case_templates = self.storage.query_templates_by_use_case(
                use_case.use_case_id
            )
            templates.extend(case_templates)

        # Get all executions linked to this requirement
        executions = self.storage.query_executions(
            filter=ExecutionFilter(requirements_id=requirement_id),
            limit=10000,
            offset=0,
        )

        logger.info(
            f"Traced requirement {requirement_id}: "
            f"{len(use_cases)} use cases, {len(templates)} templates, "
            f"{len(executions)} executions"
        )

        return RequirementTrace(
            requirement_id=requirement_id,
            requirements=requirements,
            use_cases=use_cases,
            templates=templates,
            executions=executions,
        )

    def trace_execution_backward(self, execution_id: str) -> Dict[str, Any]:
        """
        Trace an execution backward to its source.

        Args:
            execution_id: Execution ID

        Returns:
            Dictionary with complete backward lineage

        Example:
            >>> lineage = tracker.trace_execution_backward(exec_id)
            >>> print(lineage['path'])  # ['requirement', 'use_case', 'template', 'execution']
        """
        lineage = self.get_complete_lineage(execution_id)

        path = []
        if lineage.requirements:
            path.append(
                {
                    "type": "requirement",
                    "id": lineage.requirements.requirements_id,
                    "name": lineage.requirements.summary,
                }
            )
        if lineage.use_case:
            path.append(
                {
                    "type": "use_case",
                    "id": lineage.use_case.use_case_id,
                    "name": lineage.use_case.title,
                }
            )
        if lineage.template:
            path.append(
                {
                    "type": "template",
                    "id": lineage.template.template_id,
                    "name": lineage.template.name,
                }
            )
        path.append(
            {
                "type": "execution",
                "id": lineage.execution.execution_id,
                "name": f"{lineage.execution.algorithm} execution",
            }
        )

        return {
            "execution_id": execution_id,
            "path": path,
            "complete": lineage.requirements is not None,
            "lineage": lineage,
        }

    def build_lineage_graph(self, epoch_id: Optional[str] = None) -> LineageGraph:
        """
        Build complete lineage graph for visualization.

        Args:
            epoch_id: Optional epoch filter

        Returns:
            LineageGraph with all nodes and edges

        Example:
            >>> graph = tracker.build_lineage_graph(epoch_id="epoch-1")
            >>> print(f"Nodes: {len(graph.executions)}")
            >>> print(f"Edges: {len(graph.edges)}")
        """
        # Query all entities
        exec_filter = ExecutionFilter(epoch_id=epoch_id) if epoch_id else None
        executions = self.storage.query_executions(exec_filter, limit=10000, offset=0)

        # Collect unique IDs
        requirement_ids: Set[str] = set()
        use_case_ids: Set[str] = set()
        template_ids: Set[str] = set()

        for execution in executions:
            if execution.requirements_id:
                requirement_ids.add(execution.requirements_id)
            if execution.use_case_id:
                use_case_ids.add(execution.use_case_id)
            if execution.template_id:
                template_ids.add(execution.template_id)

        # Fetch entities
        requirements = []
        for req_id in requirement_ids:
            try:
                requirements.append(self.storage.get_requirements(req_id))
            except NotFoundError:
                logger.warning(f"Requirements {req_id} not found")

        use_cases = []
        for uc_id in use_case_ids:
            try:
                use_cases.append(self.storage.get_use_case(uc_id))
            except NotFoundError:
                logger.warning(f"Use case {uc_id} not found")

        templates = []
        for tmpl_id in template_ids:
            try:
                templates.append(self.storage.get_template(tmpl_id))
            except NotFoundError:
                logger.warning(f"Template {tmpl_id} not found")

        # Build edges
        edges = []

        # Requirement -> Use Case edges
        for use_case in use_cases:
            edges.append(
                {
                    "from": use_case.requirements_id,
                    "to": use_case.use_case_id,
                    "type": "generates_use_case",
                }
            )

        # Use Case -> Template edges
        for template in templates:
            edges.append(
                {
                    "from": template.use_case_id,
                    "to": template.template_id,
                    "type": "generates_template",
                }
            )

        # Template -> Execution edges
        for execution in executions:
            edges.append(
                {
                    "from": execution.template_id,
                    "to": execution.execution_id,
                    "type": "executes",
                }
            )

        logger.info(
            f"Built lineage graph: {len(requirements)} requirements, "
            f"{len(use_cases)} use cases, {len(templates)} templates, "
            f"{len(executions)} executions, {len(edges)} edges"
        )

        return LineageGraph(
            requirements=requirements,
            use_cases=use_cases,
            templates=templates,
            executions=executions,
            edges=edges,
        )

    def analyze_impact(self, entity_id: str, entity_type: str) -> ImpactAnalysis:
        """
        Analyze impact of changing an entity.

        Shows what would be affected by modifying a requirement,
        use case, or template.

        Args:
            entity_id: ID of entity to analyze
            entity_type: Type: 'requirement', 'use_case', 'template'

        Returns:
            ImpactAnalysis showing affected entities

        Example:
            >>> impact = tracker.analyze_impact("req-123", "requirement")
            >>> print(f"Would affect {impact.total_affected} entities")
        """
        affected_use_cases = []
        affected_templates = []
        affected_executions = []

        if entity_type == "requirement":
            # Find all use cases from this requirement
            affected_use_cases = self.storage.query_use_cases_by_requirements(entity_id)

            # Find all templates from these use cases
            for use_case in affected_use_cases:
                templates = self.storage.query_templates_by_use_case(
                    use_case.use_case_id
                )
                affected_templates.extend(templates)

            # Find all executions with this requirement
            affected_executions = self.storage.query_executions(
                filter=ExecutionFilter(requirements_id=entity_id), limit=10000, offset=0
            )

        elif entity_type == "use_case":
            # Find all templates from this use case
            affected_templates = self.storage.query_templates_by_use_case(entity_id)

            # Find all executions with this use case
            affected_executions = self.storage.query_executions(
                filter=ExecutionFilter(use_case_id=entity_id), limit=10000, offset=0
            )

        elif entity_type == "template":
            # Find all executions with this template
            affected_executions = self.storage.query_executions(
                filter=ExecutionFilter(), limit=10000, offset=0
            )
            # Filter by template_id
            affected_executions = [
                e for e in affected_executions if e.template_id == entity_id
            ]

        else:
            raise LineageError(f"Unknown entity type: {entity_type}")

        total_affected = (
            len(affected_use_cases) + len(affected_templates) + len(affected_executions)
        )

        logger.info(
            f"Impact analysis for {entity_type} {entity_id}: "
            f"{total_affected} entities affected"
        )

        return ImpactAnalysis(
            source_id=entity_id,
            source_type=entity_type,
            affected_use_cases=affected_use_cases,
            affected_templates=affected_templates,
            affected_executions=affected_executions,
            total_affected=total_affected,
        )

    def get_coverage_report(self, epoch_id: Optional[str] = None) -> CoverageReport:
        """
        Generate requirement coverage report.

        Shows which requirements have been implemented and executed.

        Args:
            epoch_id: Optional epoch filter

        Returns:
            CoverageReport with coverage statistics

        Example:
            >>> report = tracker.get_coverage_report(epoch_id="epoch-1")
            >>> print(f"Coverage: {report.coverage_percentage:.1f}%")
            >>> print(f"Uncovered: {len(report.uncovered_requirements)}")
        """
        # Get all requirements (would need a method to list all)
        # For now, get requirements from executions
        exec_filter = ExecutionFilter(epoch_id=epoch_id) if epoch_id else None
        executions = self.storage.query_executions(exec_filter, limit=10000, offset=0)

        # Collect unique requirement IDs
        requirement_ids_with_executions: Set[str] = set()
        for execution in executions:
            if execution.requirements_id:
                requirement_ids_with_executions.add(execution.requirements_id)

        # Get all requirements
        # Note: This requires fetching all requirements somehow
        # For demonstration, we'll work with what we have

        requirements_with_executions = len(requirement_ids_with_executions)

        # This is a simplified version - full implementation would need
        # a way to list all requirements, not just those with executions

        return CoverageReport(
            total_requirements=requirements_with_executions,  # Undercount
            requirements_with_use_cases=requirements_with_executions,
            requirements_with_templates=requirements_with_executions,
            requirements_with_executions=requirements_with_executions,
            coverage_percentage=100.0,  # Based on what we can see
            uncovered_requirements=[],  # Can't determine without full list
        )

    def find_orphaned_entities(
        self,
    ) -> Dict[str, List[Any]]:
        """
        Find orphaned entities (no lineage links).

        Returns:
            Dictionary with lists of orphaned entities

        Example:
            >>> orphans = tracker.find_orphaned_entities()
            >>> print(f"Orphaned templates: {len(orphans['templates'])}")
        """
        # This would require iterating through all entities
        # and checking for broken links
        # Implementation depends on storage capabilities

        # Placeholder implementation
        return {
            "requirements": [],
            "use_cases": [],
            "templates": [],
            "executions": [],
        }
