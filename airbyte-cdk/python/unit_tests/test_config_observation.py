#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import time

import pytest
from airbyte_cdk.config_observation import ConfigObserver, ObservedDict, create_connector_config_control_message, observe_connector_config
from airbyte_cdk.models import AirbyteControlConnectorConfigMessage, OrchestratorType, Type


class TestObservedDict:
    def test_update_called_on_set_item(self, mocker):
        mock_observer = mocker.Mock()
        my_observed_dict = ObservedDict(
            {"key": "value", "nested_dict": {"key": "value"}, "list_of_dict": [{"key": "value"}, {"key": "value"}]}, mock_observer
        )
        assert mock_observer.update.call_count == 0

        my_observed_dict["nested_dict"]["key"] = "new_value"
        assert mock_observer.update.call_count == 1

        # Setting the same value again should call observer's update
        my_observed_dict["key"] = "new_value"
        assert mock_observer.update.call_count == 2

        my_observed_dict["nested_dict"]["new_key"] = "value"
        assert mock_observer.update.call_count == 3

        my_observed_dict["list_of_dict"][0]["key"] = "new_value"
        assert mock_observer.update.call_count == 4

        my_observed_dict["list_of_dict"][0]["new_key"] = "new_value"
        assert mock_observer.update.call_count == 5

        my_observed_dict["new_list_of_dicts"] = [{"foo": "bar"}]
        assert mock_observer.update.call_count == 6

        my_observed_dict["new_list_of_dicts"][0]["new_key"] = "new_value"
        assert mock_observer.update.call_count == 7


class TestConfigObserver:
    def test_update(self, capsys):
        config_observer = ConfigObserver()
        config_observer.set_config(ObservedDict({"key": "value"}, config_observer))
        before_time = time.time() * 1000
        config_observer.update()
        after_time = time.time() * 1000
        captured = capsys.readouterr()
        airbyte_message = json.loads(captured.out)
        assert airbyte_message["type"] == "CONTROL"
        assert "control" in airbyte_message
        raw_control_message = airbyte_message["control"]
        assert raw_control_message["type"] == "CONNECTOR_CONFIG"
        assert raw_control_message["connectorConfig"] == {"config": dict(config_observer.config)}
        assert before_time < raw_control_message["emitted_at"] < after_time


def test_observe_connector_config(capsys):
    non_observed_config = {"foo": "bar"}
    observed_config = observe_connector_config(non_observed_config)
    observer = observed_config.observer
    assert isinstance(observed_config, ObservedDict)
    assert isinstance(observer, ConfigObserver)
    assert observed_config.observer.config == observed_config
    observed_config["foo"] = "foo"
    captured = capsys.readouterr()
    airbyte_message = json.loads(captured.out)
    assert airbyte_message["control"]["connectorConfig"] == {"config": {"foo": "foo"}}


def test_observe_already_observed_config():
    observed_config = observe_connector_config({"foo": "bar"})
    with pytest.raises(ValueError):
        observe_connector_config(observed_config)


def test_create_connector_config_control_message():
    A_CONFIG = {"config key": "config value"}

    message = create_connector_config_control_message(A_CONFIG)

    assert message.type == Type.CONTROL
    assert message.control.type == OrchestratorType.CONNECTOR_CONFIG
    assert message.control.connectorConfig == AirbyteControlConnectorConfigMessage(config=A_CONFIG)
    assert message.control.emitted_at is not None
