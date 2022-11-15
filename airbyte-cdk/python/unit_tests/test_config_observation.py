#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import time

from airbyte_cdk.config_observation import ConfigObserver, ObservedDict


class TestObservedDict:
    def test_update_called_on_set_item(self, mocker):
        mock_observer = mocker.Mock()
        my_observed_dict = ObservedDict({"key": "value"}, mock_observer)
        assert mock_observer.update.call_count == 0
        my_observed_dict["key"] = {"nested_key": "nested_value"}
        assert mock_observer.update.call_count == 1
        my_observed_dict["key"]["nested_key"] = "new_nested_value"
        assert mock_observer.update.call_count == 2
        # Setting the same value again should not call observer's update
        my_observed_dict["key"]["nested_key"] = "new_nested_value"
        assert mock_observer.update.call_count == 2

    def test_update_not_called_on_init_with_nested_fields(self, mocker):
        mock_observer = mocker.Mock()
        ObservedDict({"key": "value", "nested": {"key": "value"}}, mock_observer)
        mock_observer.update.assert_not_called()


class TestConfigObserver:
    def test_update(self, mocker, capsys):
        mock_write_config_fn = mocker.Mock()
        mock_config_path = mocker.Mock()
        config_observer = ConfigObserver(mock_config_path, mock_write_config_fn)
        config_observer.config = ObservedDict({"key": "value"}, config_observer)
        before_time = time.time() * 1000
        config_observer.update()
        after_time = time.time() * 1000
        captured = capsys.readouterr()
        raw_control_message = json.loads(captured.out)
        mock_write_config_fn.assert_called_with(config_observer.config, mock_config_path)
        assert raw_control_message["type"] == "CONNECTOR_CONFIG"
        assert raw_control_message["connectorConfig"] == {"config": dict(config_observer.config)}
        assert before_time < raw_control_message["emitted_at"] < after_time

    def test_set_config(self, mocker):
        mock_write_config_fn = mocker.Mock()
        mock_config_path = mocker.Mock()
        config_observer = ConfigObserver(mock_config_path, mock_write_config_fn)
        observed_config = ObservedDict({"key": "value"}, config_observer)
        config_observer.set_config(observed_config)
        assert config_observer.config == observed_config
        mock_write_config_fn.assert_called_once_with(observed_config, mock_config_path)
