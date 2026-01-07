"""
Abstract base class for catalog storage backends.

This abstraction allows supporting multiple storage backends
(ArangoDB, SQLite, PostgreSQL, etc.) with a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from ..models import (
    AnalysisExecution,
    AnalysisEpoch,
    ExtractedRequirements,
    GeneratedUseCase,
    AnalysisTemplate,
    ExecutionFilter,
    EpochFilter,
)


class StorageBackend(ABC):
    """
    Abstract base class for catalog storage backends.

    Implementations must provide CRUD operations for all catalog entities
    and support for queries, transactions, and thread-safe operations.
    """

    # --- Execution Operations ---

    @abstractmethod
    def insert_execution(self, execution: AnalysisExecution) -> str:
        """
        Insert a new execution record.

        Args:
            execution: Execution to insert

        Returns:
            execution_id of inserted record

        Raises:
            StorageError: If insert fails
            DuplicateError: If execution_id already exists
        """
        pass

    @abstractmethod
    async def insert_execution_async(self, execution: AnalysisExecution) -> str:
        """Async version of insert_execution."""
        pass

    @abstractmethod
    def get_execution(self, execution_id: str) -> AnalysisExecution:
        """
        Get execution by ID.

        Args:
            execution_id: Execution ID

        Returns:
            AnalysisExecution

        Raises:
            NotFoundError: If execution not found
            StorageError: If query fails
        """
        pass

    @abstractmethod
    def query_executions(
        self,
        filter: Optional[ExecutionFilter] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AnalysisExecution]:
        """
        Query executions with optional filters.

        Args:
            filter: Filter criteria
            limit: Max results to return
            offset: Offset for pagination

        Returns:
            List of AnalysisExecution matching filters

        Raises:
            StorageError: If query fails
        """
        pass

    @abstractmethod
    def update_execution(self, execution: AnalysisExecution) -> None:
        """
        Update existing execution.

        Args:
            execution: Updated execution

        Raises:
            NotFoundError: If execution not found
            StorageError: If update fails
        """
        pass

    @abstractmethod
    def delete_execution(self, execution_id: str) -> None:
        """
        Delete execution by ID.

        Args:
            execution_id: Execution ID to delete

        Raises:
            NotFoundError: If execution not found
            StorageError: If delete fails
        """
        pass

    # --- Epoch Operations ---

    @abstractmethod
    def insert_epoch(self, epoch: AnalysisEpoch) -> str:
        """Insert a new epoch."""
        pass

    @abstractmethod
    async def insert_epoch_async(self, epoch: AnalysisEpoch) -> str:
        """Async version of insert_epoch."""
        pass

    @abstractmethod
    def get_epoch(self, epoch_id: str) -> AnalysisEpoch:
        """Get epoch by ID."""
        pass

    @abstractmethod
    def get_epoch_by_name(self, name: str) -> Optional[AnalysisEpoch]:
        """Get epoch by unique name."""
        pass

    @abstractmethod
    def query_epochs(
        self, filter: Optional[EpochFilter] = None, limit: int = 100, offset: int = 0
    ) -> List[AnalysisEpoch]:
        """Query epochs with optional filters."""
        pass

    @abstractmethod
    def update_epoch(self, epoch: AnalysisEpoch) -> None:
        """Update existing epoch."""
        pass

    @abstractmethod
    def delete_epoch(self, epoch_id: str, cascade: bool = False) -> None:
        """
        Delete epoch by ID.

        Args:
            epoch_id: Epoch ID to delete
            cascade: If True, also delete all executions in this epoch
        """
        pass

    # --- Requirements Operations (for lineage) ---

    @abstractmethod
    def insert_requirements(self, requirements: ExtractedRequirements) -> str:
        """Insert extracted requirements."""
        pass

    @abstractmethod
    async def insert_requirements_async(
        self, requirements: ExtractedRequirements
    ) -> str:
        """Async version of insert_requirements."""
        pass

    @abstractmethod
    def get_requirements(self, requirements_id: str) -> ExtractedRequirements:
        """Get requirements by ID."""
        pass

    # --- Use Case Operations (for lineage) ---

    @abstractmethod
    def insert_use_case(self, use_case: GeneratedUseCase) -> str:
        """Insert generated use case."""
        pass

    @abstractmethod
    async def insert_use_case_async(self, use_case: GeneratedUseCase) -> str:
        """Async version of insert_use_case."""
        pass

    @abstractmethod
    def get_use_case(self, use_case_id: str) -> GeneratedUseCase:
        """Get use case by ID."""
        pass

    @abstractmethod
    def query_use_cases_by_requirements(
        self, requirements_id: str
    ) -> List[GeneratedUseCase]:
        """Get all use cases derived from requirements."""
        pass

    # --- Template Operations (for lineage) ---

    @abstractmethod
    def insert_template(self, template: AnalysisTemplate) -> str:
        """Insert analysis template."""
        pass

    @abstractmethod
    async def insert_template_async(self, template: AnalysisTemplate) -> str:
        """Async version of insert_template."""
        pass

    @abstractmethod
    def get_template(self, template_id: str) -> AnalysisTemplate:
        """Get template by ID."""
        pass

    @abstractmethod
    def query_templates_by_use_case(self, use_case_id: str) -> List[AnalysisTemplate]:
        """Get all templates derived from use case."""
        pass

    # --- Management Operations ---

    @abstractmethod
    def initialize_collections(self) -> None:
        """
        Initialize all required collections and indexes.

        This should be called once during setup.
        """
        pass

    @abstractmethod
    def reset(self, confirm: bool = False) -> None:
        """
        Delete all catalog data.

        Args:
            confirm: Must be True to actually reset (safety)
        """
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get catalog statistics."""
        pass

    @abstractmethod
    def export_catalog(self, output_path: str) -> None:
        """Export entire catalog to file."""
        pass

    @abstractmethod
    def import_catalog(self, input_path: str) -> None:
        """Import catalog from file."""
        pass

    # --- Connection Management ---

    @abstractmethod
    def close(self) -> None:
        """Close database connection and cleanup."""
        pass
