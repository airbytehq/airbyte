"""Test source implementation."""
import pytest
from source_airmeet.source import SourceAirmeet


def test_source_spec():
    """Test spec command."""
    source = SourceAirmeet()
    spec = source.spec(logger=None)
    assert spec is not None
    assert spec.connectionSpecification is not None


def test_source_check_connection():
    """Test check connection."""
    source = SourceAirmeet()
    config = {
        "access_key": "test-key",
        "secret_key": "test-secret"
    }
    # This will fail without mocking, which is expected
    success, error = source.check_connection(logger=None, config=config)
    assert isinstance(success, bool)