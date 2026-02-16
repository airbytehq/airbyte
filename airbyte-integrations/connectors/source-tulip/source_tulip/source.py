"""Tulip Airbyte Source Connector."""

import logging
from typing import Any, List, Mapping, Optional, Tuple

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_tulip.streams import TulipTableStream, create_api_budget
from source_tulip.utils import build_tables_url

logger = logging.getLogger("airbyte")


class SourceTulip(AbstractSource):
    """Airbyte source connector for Tulip Tables.

    Discovers all Tulip tables and exposes each as an independently
    selectable Airbyte stream with dynamic schema discovery.
    """

    def check_connection(
        self, logger: logging.Logger, config: Mapping[str, Any]
    ) -> Tuple[bool, Optional[Any]]:
        """Validate credentials by hitting the table-listing API.

        Returns (True, None) on success, (False, error_message) on failure.
        """
        for field in ("subdomain", "api_key", "api_secret"):
            if not config.get(field):
                return False, f"Missing required configuration field: {field}"

        try:
            url = build_tables_url(
                config["subdomain"], config.get("workspace_id")
            )
            response = requests.get(
                url,
                auth=(config["api_key"], config["api_secret"]),
                timeout=30,
            )
            response.raise_for_status()
            return True, None
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            return False, f"HTTP {status} from Tulip API: {e}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Could not connect to Tulip API: {e}"
        except Exception as e:
            return False, f"Connection check failed: {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """Return one TulipTableStream per Tulip table.

        Calls GET /api/v3/tables (or workspace-scoped equivalent) to
        discover all available tables, then instantiates a stream for each.
        """
        url = build_tables_url(
            config["subdomain"], config.get("workspace_id")
        )
        response = requests.get(
            url,
            auth=(config["api_key"], config["api_secret"]),
            timeout=30,
        )
        response.raise_for_status()
        tables = response.json()

        # Shared budget enforces Tulip's 50 req/s rate limit across all streams
        api_budget = create_api_budget()

        streams: List[Stream] = []
        for table in tables:
            stream = TulipTableStream(
                table_id=table["id"],
                table_label=table.get("label", table["id"]),
                table_metadata=table,
                config=config,
                api_budget=api_budget,
            )
            streams.append(stream)

        logger.info(f"Discovered {len(streams)} Tulip table(s)")
        return streams
