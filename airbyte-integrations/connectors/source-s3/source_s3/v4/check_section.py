#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
"""
Section-aware CHECK for the stepped setup form.

The spec declares `sections` (see `source_s3.v4.config.SECTIONS`), each listing the `groups` of properties it shows. The
form checks the configuration one section at a time: the configuration JSON then carries a top-level `check-section`
key naming the section, and only holds the fields of that section and of the sections before it. CHECK validates that
much only. Without the key, CHECK validates the complete configuration, exactly as before.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.models import ConnectorSpecification, FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_s3.v4.config import SECTIONS


CHECK_SECTION_KEY = "check-section"


def declared_sections() -> List[str]:
    """The `sections[].id` values of the spec, in form order."""
    return [section["id"] for section in SECTIONS]


def requested_section(config: Mapping[str, Any]) -> Optional[str]:
    """
    The section named by `check-section` in the config, or None for a full check.

    Raises a config error when the key does not name one of the declared sections.
    """
    section = config.get(CHECK_SECTION_KEY)
    if section is None:
        return None
    if not isinstance(section, str) or not section.strip():
        raise _config_error(f"'{CHECK_SECTION_KEY}' must be a non-empty string.")
    declared = declared_sections()
    if section not in declared:
        raise _config_error(f"Unknown {CHECK_SECTION_KEY} '{section}'; the connector specification declares: {', '.join(declared)}.")
    return section


def strip_check_section(config: Mapping[str, Any]) -> Dict[str, Any]:
    """The config without the `check-section` key, which is not a connector field."""
    return {key: value for key, value in config.items() if key != CHECK_SECTION_KEY}


def section_spec(spec: ConnectorSpecification, section: str) -> ConnectorSpecification:
    """
    The spec narrowed to what the form has collected by `section`: `required` only keeps the properties whose group belongs
    to that section or to an earlier one. Every property keeps its own schema, so the fields which are present are still
    validated in full. The last section completes the configuration, so its spec is the full spec.
    """
    declared = declared_sections()
    if section == declared[-1]:
        return spec
    collected_groups = {group for declared_section in SECTIONS[: declared.index(section) + 1] for group in declared_section["groups"]}
    schema = copy.deepcopy(spec.connectionSpecification)
    properties = schema.get("properties", {})
    schema["required"] = [name for name in schema.get("required", []) if properties.get(name, {}).get("group") in collected_groups]
    narrowed = copy.copy(spec)
    narrowed.connectionSpecification = schema
    return narrowed


def _config_error(message: str) -> AirbyteTracedException:
    return AirbyteTracedException(message=message, internal_message=message, failure_type=FailureType.config_error)
