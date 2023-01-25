#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops import utils

def test_get_connector_definition():
    assert utils.get_connector_definition("source-dynamodb") == {
        "name": "DynamoDB",
        "sourceDefinitionId": "50401137-8871-4c5a-abb7-1f5fda35545a",
        "dockerRepository": "airbyte/source-dynamodb",
        "dockerImageTag": "0.1.0",
        "documentationUrl": "https://docs.airbyte.com/integrations/sources/dynamodb",
        "sourceType": "api",
        "releaseStage": "alpha"
    }
