#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, List, Mapping

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.logger import PRINT_BUFFER
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config
from source_s3.v4.check_section import requested_section, section_spec, strip_check_section


class SourceS3Entrypoint(AirbyteEntrypoint):
    """
    Entrypoint which makes the config-against-spec validation of CHECK section-aware.

    A section check only carries the fields collected up to the section, so the complete spec's `required` list would
    reject it before the connector gets to look at it. The partial config is validated against the spec narrowed to that
    section instead (see `source_s3.v4.check_section.section_spec`). A config without `check-section` is validated against
    the complete spec, as before.
    """

    @staticmethod
    def validate_connection(source_spec: ConnectorSpecification, config: Mapping[str, Any]) -> None:
        section = requested_section(config)
        if section is None:
            AirbyteEntrypoint.validate_connection(source_spec, config)
            return
        connector_config, _ = split_config(strip_check_section(config))
        check_config_against_spec_or_exit(connector_config, section_spec(source_spec, section))


def launch(source: Source, args: List[str]) -> None:
    """Same as `airbyte_cdk.entrypoint.launch`, with the section-aware entrypoint."""
    source_entrypoint = SourceS3Entrypoint(source)
    parsed_args = source_entrypoint.parse_args(args)
    with PRINT_BUFFER:
        for message in source_entrypoint.run(parsed_args):
            # Print the message and its line break in one call so concurrent prints do not interleave.
            print(f"{message}\n", end="")
