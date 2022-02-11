#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pytest
import os
import json
import pendulum

from airbyte_cdk.models import Type
from source_open_exchange_rates.source import SourceOpenExchangeRates


@pytest.fixture
def assert_read_records_are_expected(oxr_app_id):
    def assert_read_records_are_expected(config_filename, catalog_filename, expected_results_filename, state_filename=None):
        """
        Read records accoring to config setup, configured_catalog and optional state
        and compare them to expected

        secrets_config_filename is used to get the OpenExchangeRates App id and replace it in the config template 
        """
        integration_tests_dirpath = os.path.dirname(os.path.realpath(__file__))

        config_filepath = os.path.sep.join([integration_tests_dirpath, "config", config_filename])
        catalog_filepath = os.path.sep.join([integration_tests_dirpath, "configured_catalog", catalog_filename])
        expected_results_filepath = os.path.sep.join([integration_tests_dirpath, "expected_results", expected_results_filename])
        state_filepath = os.path.sep.join([integration_tests_dirpath, "state", state_filename]) if state_filename is not None else None

        source = SourceOpenExchangeRates()
        
        config = source.read_config(config_filepath)
        config["app_id"] = pytest.oxr_app_id # override test config app_id with the real one located in secrets directory

        configured_catalog = source.read_catalog(catalog_filepath)
        state = source.read_state(state_filepath) if state_filepath is not None else None
        logger = source.logger

        actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog, state=state)

        with open(expected_results_filepath) as file:
            expected_messages = file.read().splitlines()


        actual_messages_json = []
        for mess in actual_messages:
            mess_json = json.loads(mess.json(exclude_none=True))
            if mess.type == Type.RECORD:
                
                # remove "emitted_at" attribute for comparison because it changes overtime
                if mess_json["record"].get("emitted_at") is not None:
                    del mess_json["record"]["emitted_at"]

            actual_messages_json.append(mess_json)
        

        expected_messages_json = []
        for row in expected_messages:
            expected_mess = json.loads(row)

            # remove "emitted_at" attribute for comparison because it changes overtime
            if expected_mess.get("record") is not None:
                if expected_mess["record"].get("emitted_at") is not None:
                    del expected_mess["record"]["emitted_at"]

            expected_messages_json.append(expected_mess)

        for i, message in enumerate(actual_messages_json):
            assert json.dumps(actual_messages_json[i], sort_keys=True)  == json.dumps(expected_messages_json[i], sort_keys=True)
        
    return assert_read_records_are_expected


def test_read_records_full_refresh_no_max_records_per_sync(assert_read_records_are_expected):
    integration_tests_dirpath = os.path.dirname(os.path.realpath(__file__))

    config_filename = "config_no_max_records_per_sync.json"
    catalog_filename = "configured_catalog_full_refresh.json"

    config_filepath = os.path.sep.join([integration_tests_dirpath, "config", config_filename])
    catalog_filepath = os.path.sep.join([integration_tests_dirpath, "configured_catalog", catalog_filename])

    source = SourceOpenExchangeRates()
    
    config = source.read_config(config_filepath)
    config["app_id"] = pytest.oxr_app_id # override test config app_id with the real one located in secrets directory
    config["start_date"] = pendulum.now(pendulum.UTC).add(days=-2).to_date_string() # set the start date to current day minus two days

    configured_catalog = source.read_catalog(catalog_filepath)
    logger = source.logger

    # Test with ignore_current_day not set (default to true)
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 2
    assert all([mess["record"].get("data") is not None for mess in actual_messages_json])
    assert all([isinstance(mess["record"]["data"].get("timestamp"), int) for mess in actual_messages_json])
    assert all([mess["record"]["data"].get("base") == config["base"] for mess in actual_messages_json])
    assert all([isinstance(mess["record"]["data"].get("rates"), dict) for mess in actual_messages_json])
    assert all([sorted(list(mess["record"]["data"]["rates"].keys())) == sorted(config["symbols"].split(",")) for mess in actual_messages_json])

    # Test with ignore_current_day set to true
    config["ignore_current_day"] = True
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 2

    # Test with ignore_current_day set to false
    config["ignore_current_day"] = False
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 3



def test_read_records_full_refresh_max_records_per_sync(assert_read_records_are_expected):
    config_filename = "config_max_records_per_sync.json"
    catalog_filename = "configured_catalog_full_refresh.json"
    expected_results_filename = "expected_messages_full_refresh_max_records_per_sync.txt"
    
    assert_read_records_are_expected(config_filename, catalog_filename, expected_results_filename)


def test_read_records_incremental_no_max_records_per_sync(assert_read_records_are_expected):
    integration_tests_dirpath = os.path.dirname(os.path.realpath(__file__))

    config_filename = "config_no_max_records_per_sync.json"
    catalog_filename = "configured_catalog_incremental.json"

    config_filepath = os.path.sep.join([integration_tests_dirpath, "config", config_filename])
    catalog_filepath = os.path.sep.join([integration_tests_dirpath, "configured_catalog", catalog_filename])

    source = SourceOpenExchangeRates()
    
    config = source.read_config(config_filepath)
    config["app_id"] = pytest.oxr_app_id # override test config app_id with the real one located in secrets directory
    config["start_date"] = pendulum.now(pendulum.UTC).add(days=-2).to_date_string() # set the start date to current day minus two days

    configured_catalog = source.read_catalog(catalog_filepath)
    logger = source.logger

    # Test with ignore_current_day not set (default to true)
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 4
    assert [mess["type"] for mess in actual_messages_json] == ['RECORD', 'STATE', 'RECORD', 'STATE']

    records = []
    states = []
    for mess in actual_messages_json:
        if mess["type"] == "RECORD":
            records.append(mess["record"])
        else:
            states.append(mess["state"])

    assert all([record.get("data") is not None for record in records])
    assert all([isinstance(record["data"].get("timestamp"), int) for record in records])
    assert all([record["data"].get("base") == config["base"] for record in records])
    assert all([isinstance(record["data"].get("rates"), dict) for record in records])
    assert all([sorted(list(record["data"]["rates"].keys())) == sorted(config["symbols"].split(",")) for record in records])


    assert all([state.get("data") is not None for state in states])
    assert all([state["data"].get("historical_exchange_rates") is not None for state in states])
    assert all([isinstance(state["data"]["historical_exchange_rates"].get("timestamp"), int) for state in states])

    for i, record in enumerate(records):
        assert records[i]["data"]["timestamp"] == states[i]["data"]["historical_exchange_rates"]["timestamp"]


    # Test with ignore_current_day set to true
    config["ignore_current_day"] = True
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 4

    # Test with ignore_current_day set to false
    config["ignore_current_day"] = False
    actual_messages = source.read(logger=logger, config=config, catalog=configured_catalog)
    actual_messages_json = [json.loads(mess.json(exclude_none=True)) for mess in actual_messages]

    assert len(actual_messages_json) == 6


def test_read_records_incremental_max_records_per_sync(assert_read_records_are_expected):
    config_filename = "config_max_records_per_sync.json"
    catalog_filename = "configured_catalog_incremental.json"
    expected_results_filename = "expected_messages_incremental_max_records_per_sync.txt"
    
    assert_read_records_are_expected(config_filename, catalog_filename, expected_results_filename)


def test_read_records_incremental_max_records_per_sync_with_state(assert_read_records_are_expected):
    config_filename = "config_max_records_per_sync.json"
    catalog_filename = "configured_catalog_incremental.json"
    expected_results_filename = "expected_messages_incremental_max_records_per_sync_with_state.txt"
    state_filename = "state_incremental_max_records_per_sync_with_state.json"

    assert_read_records_are_expected(config_filename, catalog_filename, expected_results_filename, state_filename)
