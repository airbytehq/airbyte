#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Source Marketo entry point.

All streams are now fully declarative (defined in ``manifest.yaml``).
Bulk export streams (Leads + Activities) use the CDK ``AsyncRetriever``
pattern with custom components defined in ``components.py``.
"""

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceMarketo(YamlDeclarativeSource):
    """Source Marketo — declarative connector for the Marketo REST API."""

    def __init__(self) -> None:
        super().__init__(path_to_yaml="manifest.yaml")
