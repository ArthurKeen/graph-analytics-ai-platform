"""Storage backend initialization."""

from .base import StorageBackend
from .arangodb import ArangoDBStorage

__all__ = ["StorageBackend", "ArangoDBStorage"]
