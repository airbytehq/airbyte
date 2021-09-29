#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from functools import partial
from typing import Any, Callable, Generator, Iterable, List, Mapping, Optional, Tuple

from airbyte_protocol import AirbyteStream
from base_python import AirbyteLogger, BaseClient
from grnhse import Harvest
from grnhse.exceptions import HTTPError
from grnhse.harvest.api import HarvestObject

DEFAULT_ITEMS_PER_PAGE = 100


def paginator(request: HarvestObject, **params) -> Iterable[Optional[Mapping[str, Any]]]:
    """
    Split requests in multiple batches and return records as generator.
    Use recursion in case of nested streams.
    """
    rows = request.get(**params)
    nested_names = params.pop("nested_names", None)
    if nested_names:
        if len(nested_names) > 1:
            params["nested_names"] = params["nested_names"][1:]
        for row in rows:
            yield from paginator(getattr(request(**params, object_id=row["id"]), nested_names[0]))
    else:
        yield from rows
    while request.records_remaining:
        rows = request.get_next()
        yield from rows


class HarvestClient(Harvest):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._uris["direct"] = {
            **self._uris["direct"],
            "demographics_question_sets": {"list": "demographics/question_sets", "retrieve": "demographics/question_sets/{id}"},
            "demographics_questions": {"list": "demographics/questions"},
            "demographics_answer_options": {"list": "demographics/answer_options", "retrieve": "demographics/answer_options/{id}"},
            "demographics_answers": {"list": "demographics/answers", "retrieve": "demographics/answers/{id}"},
        }
        self._uris["related"]["applications"] = {
            **self._uris["related"]["applications"],
            "demographics_answers": {"list": "applications/{rel_id}/demographics/answers"},
        }
        self._uris["related"] = {
            **self._uris["related"],
            "demographics_question_sets": {
                "questions": {
                    "list": "demographics/question_sets/{rel_id}/questions",
                    "retrieve": "demographics/question_sets/{rel_id}/questions/{{id}}",
                }
            },
            "demographics_answers": {"answer_options": {"list": "demographics/questions/{rel_id}/answer_options"}},
        }


class Client(BaseClient):
    # TODO: Adopt connector best practices https://github.com/airbytehq/airbyte/issues/1943.
    # TODO: Add the incremental support where it's possible https://github.com/airbytehq/airbyte/issues/1386.
    # TODO: Fill all streams with data https://github.com/airbytehq/airbyte/issues/6546

    ENTITIES = [
        "applications",
        "applications.demographics_answers",
        "applications.interviews",
        "candidates",
        "close_reasons",
        "custom_fields",
        "degrees",
        "demographics_answer_options",
        "demographics_answers",
        "demographics_answers.answer_options",
        "demographics_question_sets",
        "demographics_question_sets.questions",
        "demographics_questions",
        "departments",
        "interviews",
        "job_posts",
        "job_stages",
        "jobs",
        "jobs.openings",
        "jobs.stages",
        "offers",
        "rejection_reasons",
        "scorecards",
        "sources",
        "users",
    ]

    def __init__(self, api_key):
        self._client = HarvestClient(api_key=api_key)
        super().__init__()

    def list(self, name: str, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        name_parts = name.split(".")
        nested_names = name_parts[1:]
        kwargs["per_page"] = DEFAULT_ITEMS_PER_PAGE
        if nested_names:
            kwargs["nested_names"] = nested_names
        yield from paginator(getattr(self._client, name_parts[0]), **kwargs)

    def _enumerate_methods(self) -> Mapping[str, Callable]:
        return {entity: partial(self.list, name=entity) for entity in self.ENTITIES}

    def get_accessible_endpoints(self) -> List[str]:
        """
        Try to read each supported endpoint and return accessible stream names.
        Reach parent stream endpoint in case if it's nested stream endpoint.
        """
        logger = AirbyteLogger()
        accessible_endpoints = []
        for entity in self.ENTITIES:
            entity = entity.split(".")[0]
            try:
                getattr(self._client, entity).get()
                accessible_endpoints.append(entity)
            except HTTPError as error:
                logger.warn(f"Endpoint '{entity}' error: {str(error)}")
                if "This API Key does not have permission for this endpoint" not in str(error):
                    raise error
        logger.info(f"API key has access to {len(accessible_endpoints)} endpoints: {accessible_endpoints}")
        return accessible_endpoints

    def health_check(self) -> Tuple[bool, Optional[str]]:
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
