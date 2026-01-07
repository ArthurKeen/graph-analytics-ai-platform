"""
Catalog management operations.

Provides batch operations, archiving, and maintenance
capabilities for the Analysis Catalog.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path

from .models import (
    ExecutionStatus,
    EpochStatus,
    ExecutionFilter,
    EpochFilter,
)
from .storage.base import StorageBackend
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class CatalogManager:
    """
    Catalog management and maintenance operations.

    Provides batch operations, archiving, cleanup, and
    administrative functions for the catalog.
    """

    def __init__(self, storage: StorageBackend):
        """
        Initialize catalog manager.

        Args:
            storage: Storage backend
        """
        self.storage = storage

    def batch_delete_executions(
        self, filter: ExecutionFilter, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Delete multiple executions matching filter.

        Args:
            filter: Filter to match executions
            dry_run: If True, only show what would be deleted

        Returns:
            Dictionary with deletion summary

        Example:
            >>> # Preview deletion
            >>> result = manager.batch_delete_executions(
            ...     filter=ExecutionFilter(status=ExecutionStatus.FAILED),
            ...     dry_run=True
            ... )
            >>> print(f"Would delete: {result['count']}")
            >>>
            >>> # Actually delete
            >>> result = manager.batch_delete_executions(
            ...     filter=ExecutionFilter(status=ExecutionStatus.FAILED),
            ...     dry_run=False
            ... )
        """
        executions = self.storage.query_executions(filter, limit=10000, offset=0)

        result = {
            "count": len(executions),
            "dry_run": dry_run,
            "deleted_ids": [],
            "errors": [],
        }

        if not dry_run:
            for execution in executions:
                try:
                    self.storage.delete_execution(execution.execution_id)
                    result["deleted_ids"].append(execution.execution_id)
                except Exception as e:
                    result["errors"].append(
                        {
                            "execution_id": execution.execution_id,
                            "error": str(e),
                        }
                    )
                    logger.error(
                        f"Failed to delete execution {execution.execution_id}: {e}"
                    )

            logger.info(f"Deleted {len(result['deleted_ids'])} executions")

        return result

    def archive_old_epochs(
        self, older_than_days: int = 90, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Archive epochs older than threshold.

        Changes status to ARCHIVED but doesn't delete.

        Args:
            older_than_days: Archive epochs older than this
            dry_run: If True, only show what would be archived

        Returns:
            Dictionary with archival summary

        Example:
            >>> result = manager.archive_old_epochs(
            ...     older_than_days=180,
            ...     dry_run=False
            ... )
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        filter = EpochFilter(end_date=cutoff_date, status=EpochStatus.ACTIVE)

        epochs = self.storage.query_epochs(filter, limit=10000, offset=0)

        result = {
            "count": len(epochs),
            "dry_run": dry_run,
            "archived_ids": [],
            "errors": [],
        }

        if not dry_run:
            for epoch in epochs:
                try:
                    epoch.status = EpochStatus.ARCHIVED
                    self.storage.update_epoch(epoch)
                    result["archived_ids"].append(epoch.epoch_id)
                except Exception as e:
                    result["errors"].append(
                        {
                            "epoch_id": epoch.epoch_id,
                            "error": str(e),
                        }
                    )
                    logger.error(f"Failed to archive epoch {epoch.epoch_id}: {e}")

            logger.info(f"Archived {len(result['archived_ids'])} epochs")

        return result

    def cleanup_failed_executions(
        self, older_than_days: int = 30, dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Delete failed executions older than threshold.

        Args:
            older_than_days: Delete failures older than this
            dry_run: If True, only show what would be deleted

        Returns:
            Dictionary with cleanup summary

        Example:
            >>> result = manager.cleanup_failed_executions(
            ...     older_than_days=30,
            ...     dry_run=False
            ... )
        """
        cutoff_date = datetime.now() - timedelta(days=older_than_days)

        filter = ExecutionFilter(status=ExecutionStatus.FAILED, end_date=cutoff_date)

        return self.batch_delete_executions(filter, dry_run=dry_run)

    def vacuum_orphaned_data(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Remove orphaned data (entities with broken links).

        Args:
            dry_run: If True, only report orphans

        Returns:
            Dictionary with vacuum summary

        Example:
            >>> result = manager.vacuum_orphaned_data(dry_run=True)
            >>> print(f"Orphaned executions: {result['orphaned_executions']}")
        """
        # Find executions with missing templates
        all_executions = self.storage.query_executions(
            filter=None, limit=10000, offset=0
        )

        orphaned_executions = []
        for execution in all_executions:
            try:
                self.storage.get_template(execution.template_id)
            except Exception:
                orphaned_executions.append(execution.execution_id)

        result = {
            "orphaned_executions": len(orphaned_executions),
            "dry_run": dry_run,
            "deleted": [],
        }

        if not dry_run and orphaned_executions:
            for exec_id in orphaned_executions:
                try:
                    self.storage.delete_execution(exec_id)
                    result["deleted"].append(exec_id)
                except Exception as e:
                    logger.error(f"Failed to delete orphaned execution {exec_id}: {e}")

            logger.info(f"Deleted {len(result['deleted'])} orphaned executions")

        return result

    def export_epoch(
        self, epoch_id: str, output_path: str, include_results: bool = False
    ) -> Dict[str, Any]:
        """
        Export a single epoch to file.

        Args:
            epoch_id: Epoch to export
            output_path: Path to output file
            include_results: Whether to include full result data

        Returns:
            Dictionary with export summary

        Example:
            >>> manager.export_epoch(
            ...     epoch_id="epoch-123",
            ...     output_path="/backups/epoch-123.json"
            ... )
        """
        # Get epoch
        epoch = self.storage.get_epoch(epoch_id)

        # Get all executions in epoch
        executions = self.storage.query_executions(
            filter=ExecutionFilter(epoch_id=epoch_id), limit=10000, offset=0
        )

        # Build export data
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "epoch": epoch.to_dict(),
            "executions": [e.to_dict() for e in executions],
            "execution_count": len(executions),
        }

        # Write to file
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(
            f"Exported epoch {epoch_id} with {len(executions)} executions to {output_path}"
        )

        return {
            "epoch_id": epoch_id,
            "execution_count": len(executions),
            "output_path": output_path,
            "file_size_bytes": Path(output_path).stat().st_size,
        }

    def import_epoch(self, input_path: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Import epoch from file.

        Args:
            input_path: Path to import file
            overwrite: Whether to overwrite existing data

        Returns:
            Dictionary with import summary

        Example:
            >>> manager.import_epoch("/backups/epoch-123.json")
        """
        with open(input_path, "r") as f:
            import_data = json.load(f)

        # Import epoch
        from .models import AnalysisEpoch, AnalysisExecution

        epoch = AnalysisEpoch.from_dict(import_data["epoch"])

        # Check if exists
        try:
            existing = self.storage.get_epoch(epoch.epoch_id)
            if existing and not overwrite:
                raise ValidationError(
                    f"Epoch {epoch.epoch_id} already exists. Use overwrite=True"
                )
        except Exception:
            pass

        # Insert epoch
        self.storage.insert_epoch(epoch)

        # Import executions
        imported_count = 0
        errors = []

        for exec_dict in import_data["executions"]:
            try:
                execution = AnalysisExecution.from_dict(exec_dict)
                self.storage.insert_execution(execution)
                imported_count += 1
            except Exception as e:
                errors.append(
                    {"execution_id": exec_dict.get("execution_id"), "error": str(e)}
                )
                logger.error(f"Failed to import execution: {e}")

        logger.info(f"Imported epoch {epoch.epoch_id} with {imported_count} executions")

        return {
            "epoch_id": epoch.epoch_id,
            "executions_imported": imported_count,
            "errors": len(errors),
            "error_details": errors,
        }

    def get_storage_usage(self) -> Dict[str, Any]:
        """
        Get storage usage statistics.

        Returns:
            Dictionary with storage metrics

        Example:
            >>> usage = manager.get_storage_usage()
            >>> print(f"Total executions: {usage['execution_count']}")
        """
        stats = self.storage.get_statistics()

        # Get all executions to calculate data sizes
        all_executions = self.storage.query_executions(
            filter=None, limit=10000, offset=0
        )

        # Estimate data sizes (rough approximation)
        total_results = sum(e.result_count for e in all_executions)

        return {
            "execution_count": stats["total_executions"],
            "epoch_count": stats["total_epochs"],
            "total_result_documents": total_results,
            "algorithms": stats["execution_count_by_algorithm"],
            "estimated_storage_mb": total_results * 0.001,  # Rough estimate
        }

    def validate_catalog_integrity(self) -> Dict[str, Any]:
        """
        Validate catalog data integrity.

        Checks for:
        - Broken lineage links
        - Missing referenced entities
        - Invalid data

        Returns:
            Dictionary with validation results

        Example:
            >>> integrity = manager.validate_catalog_integrity()
            >>> if integrity['errors']:
            ...     print("Integrity issues found!")
        """
        errors = []
        warnings = []

        # Get all executions
        executions = self.storage.query_executions(filter=None, limit=10000, offset=0)

        # Check each execution
        for execution in executions:
            # Check template exists
            try:
                self.storage.get_template(execution.template_id)
            except Exception:
                errors.append(
                    {
                        "type": "missing_template",
                        "execution_id": execution.execution_id,
                        "template_id": execution.template_id,
                    }
                )

            # Check optional lineage
            if execution.use_case_id:
                try:
                    self.storage.get_use_case(execution.use_case_id)
                except Exception:
                    warnings.append(
                        {
                            "type": "missing_use_case",
                            "execution_id": execution.execution_id,
                            "use_case_id": execution.use_case_id,
                        }
                    )

            if execution.requirements_id:
                try:
                    self.storage.get_requirements(execution.requirements_id)
                except Exception:
                    warnings.append(
                        {
                            "type": "missing_requirements",
                            "execution_id": execution.execution_id,
                            "requirements_id": execution.requirements_id,
                        }
                    )

            # Check epoch if specified
            if execution.epoch_id:
                try:
                    self.storage.get_epoch(execution.epoch_id)
                except Exception:
                    warnings.append(
                        {
                            "type": "missing_epoch",
                            "execution_id": execution.execution_id,
                            "epoch_id": execution.epoch_id,
                        }
                    )

        logger.info(
            f"Integrity check complete: {len(errors)} errors, {len(warnings)} warnings"
        )

        return {
            "executions_checked": len(executions),
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "healthy": len(errors) == 0,
        }

    def repair_catalog(
        self, fix_orphans: bool = False, fix_links: bool = False
    ) -> Dict[str, Any]:
        """
        Attempt to repair catalog issues.

        Args:
            fix_orphans: Remove orphaned executions
            fix_links: Attempt to repair broken links

        Returns:
            Dictionary with repair results

        Example:
            >>> result = manager.repair_catalog(
            ...     fix_orphans=True,
            ...     fix_links=False
            ... )
        """
        integrity = self.validate_catalog_integrity()

        repairs = {
            "orphans_removed": 0,
            "links_fixed": 0,
            "errors": [],
        }

        if fix_orphans:
            # Remove executions with missing templates
            for error in integrity["errors"]:
                if error["type"] == "missing_template":
                    try:
                        self.storage.delete_execution(error["execution_id"])
                        repairs["orphans_removed"] += 1
                    except Exception as e:
                        repairs["errors"].append(str(e))

        logger.info(f"Catalog repair complete: {repairs}")

        return repairs
