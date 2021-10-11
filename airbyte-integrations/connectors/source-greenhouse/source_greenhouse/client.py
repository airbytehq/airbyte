#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from functools import partial
from typing import Generator, List, Mapping, Tuple

from airbyte_protocol import AirbyteStream
from base_python import AirbyteLogger, BaseClient
from grnhse import Harvest
from grnhse.exceptions import HTTPError

DEFAULT_ITEMS_PER_PAGE = 100


def paginator(request, **params):
    """Split requests in multiple batches and return records as generator"""
    rows = request.get(**params)
    yield from rows
    while request.records_remaining:
        rows = request.get_next()
        yield from rows


class Client(BaseClient):
    ENTITIES = [
        "applications",
        "candidates",
        "close_reasons",
        "degrees",
        "departments",
        "job_posts",
        "jobs",
        "offers",
        "scorecards",
        "users",
        "custom_fields",
    ]

    def __init__(self, api_key):
        self._client = Harvest(api_key=api_key)
        super().__init__()

    def list(self, name, **kwargs):
        yield from paginator(getattr(self._client, name), **kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {entity: partial(self.list, name=entity) for entity in self.ENTITIES}

    def get_accessible_endpoints(self) -> List[str]:
        """Try to read each supported endpoint and return accessible stream names"""
        logger = AirbyteLogger()
        accessible_endpoints = []
        for entity in self.ENTITIES:
            try:
                getattr(self._client, entity).get()
                accessible_endpoints.append(entity)
            except HTTPError as error:
                logger.warn(f"Endpoint '{entity}' error: {str(error)}")
                if "This API Key does not have permission for this endpoint" not in str(error):
                    raise error
        logger.info(f"API key has access to {len(accessible_endpoints)} endpoints: {accessible_endpoints}")
        return accessible_endpoints

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None
        try:
            accessible_endpoints = self.get_accessible_endpoints()
            if not accessible_endpoints:
                alive = False
                error_msg = "Your API Key does not have permission for any existing endpoints. Please grant read permissions for required streams/endpoints"

        except HTTPError as error:
            alive = False
            error_msg = str(error)

        return alive, error_msg

    @property
    def streams(self) -> Generator[AirbyteStream, None, None]:
        """Process accessible streams only"""
        accessible_endpoints = self.get_accessible_endpoints()
        for stream in super().streams:
            if stream.name in accessible_endpoints:
                yield stream
