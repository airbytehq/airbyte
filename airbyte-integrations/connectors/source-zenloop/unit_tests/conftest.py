#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def config():
    return {"api_token": "<Your API Key>", "date_from": "2021-07-01", "survey_id": "<survey_id>", "survey_group_id": "<survey_group_id>"}
