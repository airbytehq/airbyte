"""Airbyte source for SAP, powered by the ERPL DuckDB extensions.

`SourceSap` is re-exported here because Airbyte's standard connector tests
locate the source class by package name -- `source_sap.SourceSap` -- rather than
by an entry point.
"""

from source_sap.source import SourceSap

__all__ = ["SourceSap"]
