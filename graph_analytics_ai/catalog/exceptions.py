"""
Custom exceptions for the Analysis Catalog system.

These exceptions provide clear error handling and help with debugging
catalog operations.
"""


class CatalogError(Exception):
    """
    Base exception for all catalog-related errors.

    All catalog-specific exceptions inherit from this base class,
    making it easy to catch any catalog error.
    """

    pass


class StorageError(CatalogError):
    """
    Raised when storage backend operations fail.

    This includes database connection errors, transaction failures,
    and other storage-related issues.

    Example:
        >>> try:
        ...     catalog.track_execution(execution)
        ... except StorageError as e:
        ...     logger.error(f"Failed to store execution: {e}")
        ...     # Handle gracefully - don't crash workflow
    """

    pass


class ValidationError(CatalogError):
    """
    Raised when data validation fails.

    This occurs when required fields are missing, data types are incorrect,
    or business logic constraints are violated.

    Example:
        >>> try:
        ...     catalog.create_epoch("")  # Empty name
        ... except ValidationError as e:
        ...     print(f"Validation error: {e}")
    """

    pass


class NotFoundError(CatalogError):
    """
    Raised when a requested entity is not found.

    This occurs when querying for an execution, epoch, or other entity
    that doesn't exist in the catalog.

    Example:
        >>> try:
        ...     execution = catalog.get_execution("nonexistent-id")
        ... except NotFoundError:
        ...     print("Execution not found")
    """

    pass


class DuplicateError(CatalogError):
    """
    Raised when attempting to create a duplicate entity.

    This occurs when trying to create an entity with a unique constraint
    violation (e.g., epoch with duplicate name).

    Example:
        >>> try:
        ...     catalog.create_epoch("2026-01")  # Already exists
        ... except DuplicateError:
        ...     print("Epoch already exists")
    """

    pass


class LineageError(CatalogError):
    """
    Raised when lineage tracking or queries fail.

    This occurs when lineage relationships are broken or invalid.
    """

    pass


class AlertError(CatalogError):
    """
    Raised when alert operations fail.

    This includes alert rule creation, evaluation, or triggering failures.
    """

    pass


class QueryError(CatalogError):
    """
    Raised when query operations fail.

    This occurs when query filters are invalid or queries cannot be executed.
    """

    pass
