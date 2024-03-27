#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import StreamSlice
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_surveymonkey.source import SourceSurveymonkey


@pytest.fixture(name='read_json')
def read_json_fixture(request):
    def read_json(file_name, skip_folder=False):
        if not skip_folder:
            folder_name = request.node.fspath.basename.split('.')[0]
        with open("unit_tests/" + folder_name + "/" + file_name) as f:
            return json.load(f)
    return read_json

@pytest.fixture(name='read_records')
def read_records_fixture(config):
    def read_records(stream_name, slice=StreamSlice(partition={"survey_id": "307785415"}, cursor_slice={})):
        stream = next(filter(lambda x: x.name == stream_name, SourceSurveymonkey().streams(config=config)))
        records = list(
            map(lambda record: record.data, stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)))
        return records
    return read_records


@pytest.fixture
def args_mock():
    return {
        "authenticator": NoAuth(),
        "start_date": pendulum.parse("2000-01-01"),
        "survey_ids": []
    }

@pytest.fixture
def config(args_mock):
    return {
        **args_mock,
        "survey_ids": ["307785415"],
        "credentials": {"access_token": "access_token"},
        "start_date": args_mock["start_date"].to_iso8601_string()
    }
