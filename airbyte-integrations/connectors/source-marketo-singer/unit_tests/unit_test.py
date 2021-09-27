#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from base_python import AirbyteLogger
from source_marketo_singer import SourceMarketoSinger

logger = AirbyteLogger()
source = SourceMarketoSinger()
catalog = "/tmp/catalog.json"
config = "/tmp/config.json"
state = "/tmp/state.json"


def test_discover_cmd():
    assert f"tap-marketo --config {config} --discover" == source.discover_cmd(logger, config).strip()


def test_read_cmd_no_state():
    assert f"tap-marketo --config {config} --properties {catalog}" == source.read_cmd(logger, config, catalog).strip()


def test_read_cmd_with_state():
    assert (
        f"tap-marketo --config {config} --properties {catalog} --state {state}" == source.read_cmd(logger, config, catalog, state).strip()
    )
