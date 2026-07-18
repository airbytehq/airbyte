# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml
from freezegun import freeze_time

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation


_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"
_EXPECTED_TEMPLATE = "{{ config.get('start_date', (now_utc() - duration('P1Y')).strftime('%Y-%m-%dT%H:%M:%SZ')) }}"


def _collect_start_datetime_templates(node):
    templates = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "start_datetime":
                if isinstance(value, str):
                    templates.append(value)
                elif isinstance(value, dict) and isinstance(value.get("datetime"), str):
                    templates.append(value["datetime"])
            templates.extend(_collect_start_datetime_templates(value))
    elif isinstance(node, list):
        for item in node:
            templates.extend(_collect_start_datetime_templates(item))
    return templates


def test_manifest_uses_one_year_default_for_every_stream():
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    templates = _collect_start_datetime_templates(manifest)

    assert templates, "Expected to find start_datetime templates in the manifest"
    assert all(template == _EXPECTED_TEMPLATE for template in templates)


@freeze_time("2024-06-15T12:00:00Z")
def test_blank_start_date_defaults_to_one_year_back():
    result = JinjaInterpolation().eval(_EXPECTED_TEMPLATE, config={})
    assert result == "2023-06-15T12:00:00Z"


@freeze_time("2024-06-15T12:00:00Z")
def test_configured_start_date_is_left_unchanged():
    result = JinjaInterpolation().eval(_EXPECTED_TEMPLATE, config={"start_date": "2020-01-01T00:00:00Z"})
    assert result == "2020-01-01T00:00:00Z"
