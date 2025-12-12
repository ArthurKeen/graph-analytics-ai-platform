"""
Top-level conftest to share fixtures across AI unit tests.
"""

pytest_plugins = [
    "tests.unit.ai.documents.conftest",
    "tests.unit.ai.schema.conftest",
]
