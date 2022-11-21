#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import time

import pytest
from airbyte_cdk.config_observation import ConfigObserver, ObservedDict, observe_connector_config


class TestObservedDict:
    def test_update_called_on_set_item(self, mocker):
        mock_observer = mocker.Mock()
        my_observed_dict = ObservedDict({"key": "value"}, mock_observer)
        assert mock_observer.update.call_count == 0
        my_observed_dict["key"] = {"nested_key": "nested_value"}
        assert mock_observer.update.call_count == 1
        my_observed_dict["key"]["nested_key"] = "new_nested_value"
        assert mock_observer.update.call_count == 2
        # Setting the same value again should call observer's update
        my_observed_dict["key"]["nested_key"] = "new_nested_value"
        assert mock_observer.update.call_count == 3

    def test_update_not_called_on_init_with_nested_fields(self, mocker):
        mock_observer = mocker.Mock()
        ObservedDict({"key": "value", "nested": {"nested_key": "nested_value"}}, mock_observer)
        mock_observer.update.assert_not_called()


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
