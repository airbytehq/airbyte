#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http.error_handlers import (
    ErrorHandler,
    HttpStatusErrorHandler,
)
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import (
    DEFAULT_ERROR_MAPPING,
)
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    ErrorResolution,
    FailureType,
    ResponseAction,
)
from airbyte_cdk.sources.streams.http.http_client import HttpClient
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


# Fields returned by the deprecated `GET /projects/` endpoint but dropped by the
# org-scoped `GET /organizations/{org}/projects/` endpoint. They are still served by
# the project detail endpoint (`GET /projects/{org}/{project}/`), so we backfill them.
ENRICHMENT_FIELDS = ("avatar", "color", "isInternal", "isPublic", "organization", "status")


@dataclass
class ProjectDetailEnrichmentTransformation(RecordTransformation):
    """
    Backfills fields on `projects` records that the org-scoped list endpoint no longer returns.

    The org-scoped endpoint `GET /organizations/{org}/projects/` omits `avatar`, `color`,
    `isInternal`, `isPublic`, `organization`, and `status`, all of which the deprecated
    `GET /projects/` endpoint used to include. For each project this transformation fetches
    `GET /projects/{org}/{slug}/` (the same endpoint the `project_detail` stream uses) and
    merges the missing fields back into the record, preserving the pre-existing schema.
    """

    config: Config
    name = "projects_detail_enrichment"
    max_retries = 5
    max_time = 60 * 10

    def __post_init__(self) -> None:
        self.logger = logging.getLogger("airbyte")
        self._hostname = self.config.get("hostname") or "sentry.io"
        self._organization = self.config["organization"]
        self._auth_token = self.config["auth_token"]
        self._url_base = f"https://{self._hostname}/api/0/"
        self._cache: dict[str, Mapping[str, Any]] = {}
        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self._get_error_handler(),
            api_budget=APIBudget(policies=[]),
            message_repository=InMemoryMessageRepository(),
        )

    def transform(
        self,
        record: dict,
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        slug = record.get("slug")
        if not slug:
            return
        detail = self._fetch_project_detail(slug)
        if not detail:
            return
        for key in ENRICHMENT_FIELDS:
            if key in detail:
                record[key] = detail[key]

    def _fetch_project_detail(self, slug: str) -> Optional[Mapping[str, Any]]:
        if slug in self._cache:
            return self._cache[slug]
        url = f"{self._url_base}projects/{self._organization}/{slug}/"
        _, response = self._http_client.send_request(
            url=url,
            request_kwargs={},
            headers={"Accept": "application/json", "Authorization": f"Bearer {self._auth_token}"},
            http_method="GET",
        )
        if response is None or not response.ok:
            self._cache[slug] = {}
            return {}
        detail = response.json()
        self._cache[slug] = detail
        return detail

    def _get_error_handler(self) -> ErrorHandler:
        # Enrichment must never fail the sync: if the detail endpoint is forbidden or the
        # project is gone, skip the backfill and keep the base record.
        error_mapping = DEFAULT_ERROR_MAPPING | {
            403: ErrorResolution(ResponseAction.IGNORE, FailureType.config_error, "Project detail forbidden. Skipping enrichment."),
            404: ErrorResolution(ResponseAction.IGNORE, FailureType.config_error, "Project not found. Skipping enrichment."),
        }
        return HttpStatusErrorHandler(logger=self.logger, error_mapping=error_mapping, max_retries=self.max_retries)
