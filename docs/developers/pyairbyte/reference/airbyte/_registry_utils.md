---
sidebar_label: _registry_utils
title: airbyte._registry_utils
---

@private Utility functions for working with the Airbyte connector registry.

## logging

## re

## requests

#### logger

#### parse\_changelog\_html

```python
def parse_changelog_html(
        html_content: str,
        connector_name: str) -> list[dict[str, str | list[str] | None]]
```

Parse changelog HTML to extract version history.

Returns a list of dicts with keys: version, release_date, docker_image_url,
changelog_url, pr_url, pr_title, parsing_errors.

#### fetch\_registry\_version\_date

```python
def fetch_registry_version_date(connector_name: str,
                                version: str) -> str | None
```

Fetch the release date for a specific version from the registry.

Returns the release date string (YYYY-MM-DD) if found, None otherwise.

