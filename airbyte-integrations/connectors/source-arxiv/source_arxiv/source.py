#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .constants import DEFAULT_MAX_RESULTS_PER_PAGE, MAX_RESULTS_PER_PAGE
from .streams import CategoriesStream, PapersStream


class SourceArxiv(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        search_query = config.get("search_query")
        if not search_query:
            return False, "The `search_query` field is required."

        try:
            max_results_per_page = int(config.get("max_results_per_page", DEFAULT_MAX_RESULTS_PER_PAGE))
        except (TypeError, ValueError):
            return False, "`max_results_per_page` must be an integer."
        if max_results_per_page < 1 or max_results_per_page > MAX_RESULTS_PER_PAGE:
            return False, f"`max_results_per_page` must be between 1 and {MAX_RESULTS_PER_PAGE}."

        try:
            probe_config = dict(config)
            probe_config["max_results_per_page"] = 1
            probe_config.pop("start_date", None)
            stream = PapersStream(config=probe_config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records, None)
            return True, None
        except Exception as exc:
            if logger:
                logger.exception("Failed to connect to the arXiv API")
            return False, str(exc)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [PapersStream(config=config), CategoriesStream()]
