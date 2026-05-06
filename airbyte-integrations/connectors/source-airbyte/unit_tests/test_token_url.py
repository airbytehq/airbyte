# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml
from jinja2 import Environment


def _render_template(template_str: str, config: dict) -> str:
    env = Environment()
    return env.from_string(template_str).render(config=config)


def _get_login_requester_url_base(manifest_path: Path) -> str:
    manifest = yaml.safe_load(manifest_path.read_text())
    return manifest["definitions"]["base_requester"]["authenticator"]["login_requester"]["url_base"]


@pytest.mark.parametrize(
    "config, expected_url",
    [
        pytest.param(
            {"client_id": "x", "client_secret": "y"},
            "https://api.airbyte.com/v1/applications/token",
            id="cloud",
        ),
        pytest.param(
            {"host": "my-airbyte.example.com", "client_id": "x", "client_secret": "y"},
            "https://my-airbyte.example.com/api/public/v1/applications/token",
            id="self_managed",
        ),
    ],
)
def test_token_url_has_no_double_slash(manifest_path: Path, config: dict, expected_url: str) -> None:
    """Regression test: token endpoint URL must not contain a double slash (see PR #77697)."""
    template = _get_login_requester_url_base(manifest_path)
    url = _render_template(template, config=config)

    assert "//" not in url.split("://", 1)[1], f"Token URL contains a double slash: {url}"
    assert url == expected_url
