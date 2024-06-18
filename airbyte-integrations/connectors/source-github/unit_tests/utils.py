#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, MutableMapping
from unittest import mock

import responses
from airbyte_cdk.models import SyncMode
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]):
    res = []
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=slice, stream_state=stream_state)
        for record in records:
            stream_state = stream_instance._get_updated_state(stream_state, record)
            res.append(record)
    return res


class ProjectsResponsesAPI:
    """
    Fake Responses API for github projects, columns, cards
    """

    projects_url = "https://api.github.com/repos/organization/repository/projects"
    columns_url = "https://api.github.com/projects/{project_id}/columns"
    cards_url = "https://api.github.com/projects/columns/{column_id}/cards"

    @classmethod
    def get_json_projects(cls, data):
        res = []
        for n, project in enumerate(data, start=1):
            name = f"project_{n}"
            res.append({"id": n, "name": name, "updated_at": project["updated_at"]})
        return res

    @classmethod
    def get_json_columns(cls, project, project_id):
        res = []
        for n, column in enumerate(project.get("columns", []), start=1):
            column_id = int(str(project_id) + str(n))
            name = f"column_{column_id}"
            res.append({"id": column_id, "name": name, "updated_at": column["updated_at"]})
        return res

    @classmethod
    def get_json_cards(cls, column, column_id):
        res = []
        for n, card in enumerate(column.get("cards", []), start=1):
            card_id = int(str(column_id) + str(n))
            name = f"card_{card_id}"
            res.append({"id": card_id, "name": name, "updated_at": card["updated_at"]})
        return res

    @classmethod
    def register(cls, data):
        responses.upsert("GET", cls.projects_url, json=cls.get_json_projects(data))
        for project_id, project in enumerate(data, start=1):
            responses.upsert("GET", cls.columns_url.format(project_id=project_id), json=cls.get_json_columns(project, project_id))
            for n, column in enumerate(project.get("columns", []), start=1):
                column_id = int(str(project_id) + str(n))
                responses.upsert("GET", cls.cards_url.format(column_id=column_id), json=cls.get_json_cards(column, column_id))


def command_check(source: Source, config):
    logger = mock.MagicMock()
    connector_config, _ = split_config(config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)
