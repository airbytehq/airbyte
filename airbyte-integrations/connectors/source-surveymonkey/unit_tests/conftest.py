#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import pendulum
import pytest
from source_surveymonkey import SourceSurveymonkey

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice


@pytest.fixture(name="read_json")
def read_json_fixture(request):
    def read_json(file_name, skip_folder=False):
        if not skip_folder:
            folder_name = request.node.fspath.basename.split(".")[0]
        with open("unit_tests/" + folder_name + "/" + file_name) as f:
            return json.load(f)

    return read_json


@pytest.fixture
def args_mock():
    return {"authenticator": None, "start_date": pendulum.parse("2000-01-01"), "survey_ids": []}


@pytest.fixture
def config(args_mock):
    return {
        **args_mock,
        "survey_ids": ["307785415"],
        "credentials": {"access_token": "access_token"},
        "start_date": args_mock["start_date"].to_iso8601_string(),
    }


@pytest.fixture
def read_records(config):
    def _read_records(stream_name, slice=StreamSlice(partition={"survey_id": "307785415"}, cursor_slice={})):
        source = SourceSurveymonkey(catalog=None, config=config, state=None)
        stream = next(filter(lambda x: x.name == stream_name, source.streams(config=config)))

        # Use CDK v7 pattern - generate_partitions instead of stream_slices
        records = []
        try:
            for partition in stream.generate_partitions():
                records.extend(list(partition.read()))
        except AttributeError:
            records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice))
        return records

    return _read_records
