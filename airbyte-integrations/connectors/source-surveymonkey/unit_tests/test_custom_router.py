#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import Mock

import pytest
from source_surveymonkey.components import SurveyIdPartitionRouter

from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig


# test cases as a list of tuples (survey_ids, parent_stream_configs, expected_slices)
test_cases = [
    (
        # test form ids present in config
        ["survey_id_1", "survey_id_2"],
        [{"stream": Mock(read_records=Mock(return_value=[{"id": "survey_id_3"}, {"id": "survey_id_4"}]))}],
        [{"survey_id": "survey_id_1"}, {"survey_id": "survey_id_2"}],
    ),
    (
        # test no form ids in config
        [],
        [
            {"stream": Mock(read_records=Mock(return_value=[{"id": "survey_id_3"}, {"id": "survey_id_4"}]))},
            {"stream": Mock(read_records=Mock(return_value=[{"id": "survey_id_5"}, {"id": "survey_id_6"}]))},
        ],
        [{"survey_id": "survey_id_3"}, {"survey_id": "survey_id_4"}, {"survey_id": "survey_id_5"}, {"survey_id": "survey_id_6"}],
    ),
]


@pytest.mark.parametrize("survey_ids, parent_stream_configs, expected_slices", test_cases)
def test_stream_slices(survey_ids, parent_stream_configs, expected_slices):
    stream_configs = []

    for parent_stream_config in parent_stream_configs:
        stream_config = ParentStreamConfig(
            stream=parent_stream_config["stream"], parent_key="id", partition_field="survey_id", config=None, parameters=None
        )
        stream_configs.append(stream_config)
    if not stream_configs:
        stream_configs = [None]

    router = SurveyIdPartitionRouter(config={"survey_ids": survey_ids}, parent_stream_configs=stream_configs, parameters=None)
    slices = list(router.stream_slices())

    assert slices == expected_slices
