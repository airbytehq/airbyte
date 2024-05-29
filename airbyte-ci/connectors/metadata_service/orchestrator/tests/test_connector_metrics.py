# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from orchestrator.assets.connector_metrics import _convert_json_to_metrics_dict


def test_convert_json_to_metrics_dict():
    jsonl_string = (
        '{"_airbyte_ab_id":"4043ed5a-2fea-4edd-8e42-5fafb5521bae","_airbyte_emitted_at":1716765524746,"_airbyte_data":{"connector_type":"destination","connector_definition_id":"0b75218b-f702-4a28-85ac-34d3d84c0fc2","connector_name":"Chroma","docker_repository":"airbyte/destination-chroma","airbyte_platform":"all","connector_version":"all","sync_success_rate":"low","usage":"medium"}}\n'
        '{"_airbyte_ab_id":"b99b6003-551a-4732-8ef5-dab626745977","_airbyte_emitted_at":1716765524746,"_airbyte_data":{"connector_type":"destination","connector_definition_id":"0b75218b-f702-4a28-85ac-34d3d84c0fc2","connector_name":"Chroma","docker_repository":"airbyte/destination-chroma","airbyte_platform":"oss","connector_version":"0.0.10","sync_success_rate":"low","usage":"medium"}}\n'
        '{"_airbyte_ab_id":"753037c6-80d8-408b-93b6-135b94e75361","_airbyte_emitted_at":1716765524746,"_airbyte_data":{"connector_type":"source","connector_definition_id":"28ce1fbd-1e15-453f-aa9f-da6c4d928e92","connector_name":"Vantage","docker_repository":"airbyte/source-vantage","airbyte_platform":"oss","connector_version":"0.1.0","sync_success_rate":"low","usage":"medium"}}\n'
        '{"_airbyte_ab_id":"a5d8989c-5944-48ea-b80b-8a69baef6f15","_airbyte_emitted_at":1716765524746,"_airbyte_data":{"connector_type":"source","connector_definition_id":"28ce1fbd-1e15-453f-aa9f-da6c4d928e92","connector_name":"Vantage","docker_repository":"airbyte/source-vantage","airbyte_platform":"cloud","connector_version":"0.1.0","sync_success_rate":"low","usage":"medium"}}\n'
        '{"_airbyte_ab_id":"4204f086-b8f9-4b74-94bb-13d418d4724d","_airbyte_emitted_at":1716765524746,"_airbyte_data":{"connector_type":"source","connector_definition_id":"28ce1fbd-1e15-453f-aa9f-da6c4d928e92","connector_name":"Vantage","docker_repository":"airbyte/source-vantage","airbyte_platform":"all","connector_version":"all","sync_success_rate":"low","usage":"medium"}}\n'
    )

    expected_metrics_dict = {
        "0b75218b-f702-4a28-85ac-34d3d84c0fc2": {
            "all": {
                "connector_type": "destination",
                "connector_definition_id": "0b75218b-f702-4a28-85ac-34d3d84c0fc2",
                "connector_name": "Chroma",
                "docker_repository": "airbyte/destination-chroma",
                "airbyte_platform": "all",
                "connector_version": "all",
                "sync_success_rate": "low",
                "usage": "medium",
            },
            "oss": {
                "connector_type": "destination",
                "connector_definition_id": "0b75218b-f702-4a28-85ac-34d3d84c0fc2",
                "connector_name": "Chroma",
                "docker_repository": "airbyte/destination-chroma",
                "airbyte_platform": "oss",
                "connector_version": "0.0.10",
                "sync_success_rate": "low",
                "usage": "medium",
            },
        },
        "28ce1fbd-1e15-453f-aa9f-da6c4d928e92": {
            "oss": {
                "connector_type": "source",
                "connector_definition_id": "28ce1fbd-1e15-453f-aa9f-da6c4d928e92",
                "connector_name": "Vantage",
                "docker_repository": "airbyte/source-vantage",
                "airbyte_platform": "oss",
                "connector_version": "0.1.0",
                "sync_success_rate": "low",
                "usage": "medium",
            },
            "cloud": {
                "connector_type": "source",
                "connector_definition_id": "28ce1fbd-1e15-453f-aa9f-da6c4d928e92",
                "connector_name": "Vantage",
                "docker_repository": "airbyte/source-vantage",
                "airbyte_platform": "cloud",
                "connector_version": "0.1.0",
                "sync_success_rate": "low",
                "usage": "medium",
            },
            "all": {
                "connector_type": "source",
                "connector_definition_id": "28ce1fbd-1e15-453f-aa9f-da6c4d928e92",
                "connector_name": "Vantage",
                "docker_repository": "airbyte/source-vantage",
                "airbyte_platform": "all",
                "connector_version": "all",
                "sync_success_rate": "low",
                "usage": "medium",
            },
        },
    }

    metrics_dict = _convert_json_to_metrics_dict(jsonl_string)

    assert metrics_dict == expected_metrics_dict
