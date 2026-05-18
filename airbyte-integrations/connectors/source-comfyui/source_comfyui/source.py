# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""ComfyUI Cloud source connector."""

import logging
from typing import Any, List, Mapping, Optional, Tuple

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import (
    AssetsStream,
    JobDetailsStream,
    JobsStream,
    ModelsStream,
    NodesStream,
    SystemStatsStream,
)


logger = logging.getLogger("airbyte")

DEFAULT_BASE_URL = "https://cloud.comfy.org"


class SourceComfyUI(AbstractSource):
    """Airbyte source connector for the ComfyUI Cloud API."""

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Validate the connection by hitting the system_stats endpoint."""
        base_url = config.get("base_url", DEFAULT_BASE_URL).rstrip("/")
        api_key = config["api_key"]

        try:
            response = requests.get(
                f"{base_url}/api/system_stats",
                headers={"X-API-Key": api_key},
                timeout=30,
            )
            response.raise_for_status()
            return True, None
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            if status == 401:
                return False, "Invalid API key. Check your key at platform.comfy.org/profile/api-keys."
            if status == 403:
                return False, "API key lacks required permissions."
            return False, f"HTTP {status}: {e}"
        except requests.exceptions.ConnectionError:
            return False, f"Could not connect to {base_url}. Verify the base URL."
        except requests.exceptions.Timeout:
            return False, f"Connection to {base_url} timed out."
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return all available streams."""
        base_url = config.get("base_url", DEFAULT_BASE_URL).rstrip("/")
        api_key = config["api_key"]

        stream_kwargs = {"api_key": api_key, "base_url": base_url}

        jobs_stream = JobsStream(**stream_kwargs)
        return [
            jobs_stream,
            JobDetailsStream(parent=jobs_stream, **stream_kwargs),
            AssetsStream(**stream_kwargs),
            ModelsStream(**stream_kwargs),
            NodesStream(**stream_kwargs),
            SystemStatsStream(**stream_kwargs),
        ]
