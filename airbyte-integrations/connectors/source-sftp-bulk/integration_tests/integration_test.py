#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from pathlib import Path
from typing import Mapping

import pytest
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)
from source_sftp_bulk import SourceFtp

pytest_plugins = ("connector_acceptance_test.plugin",)

logger = logging.getLogger("airbyte")


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        "integration_tests",
        "docker-compose.yml",
    )


@pytest.fixture(scope="session")
def ssh_path() -> Path:
    return Path(__file__).parent / "ssh" / "keys"


@pytest.fixture(scope="session")
def public_key(ssh_path: Path):
    pub_path = ssh_path / "test_source-sftp-bulk_id_rsa.pub"
    yield pub_path.read_text()


@pytest.fixture(scope="session")
def private_key(ssh_path: Path):
    priv_path = ssh_path / "test_source-sftp-bulk_id_rsa"
    yield priv_path.read_text()


@pytest.fixture(name="config", scope="session")
def config_fixture(docker_services):
    port = docker_services.port_for("mysftp", 22)

    config = {
        "host": "0.0.0.0",
        "port": port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files/json",
        "stream_name": "overwrite_stream",
        "file_most_recent": False,
        "max_depth": 0,
        "column_names": None,
        "column_names_separator": "|",
        "autogenerate_column_names": False,
        "autogenerate_column_names_prefix": "col_",
    }

    yield config


@pytest.fixture(name="config_pk", scope="session")
def config_fixture_pk(private_key, docker_services):
    available_port = docker_services.port_for("mysftpssh", 22)

    config = {
        "host": "0.0.0.0",
        "port": available_port,
        "username": "foo",
        "password": "pass",
        "file_type": "json",
        "private_key": private_key,
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "/files",
        "stream_name": "overwrite_stream",
        "file_most_recent": False,
        "max_depth": 0,
        "column_names": None,
        "column_names_separator": "|",
        "autogenerate_column_names": False,
        "autogenerate_column_names_prefix": "col_",
    }

    yield config


def get_outcome(logger: logging.Logger, config: Mapping):
    return SourceFtp().check(logger, config)


def is_responsive(
    source_ftp: SourceFtp,
    logger: logging.Logger,
    config: Mapping,
):
    try:
        outcome = SourceFtp().check(logger, config)
        if outcome.status == Status.SUCCEEDED:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def sftp_service(config, docker_services):
    """Ensure that SFTP service is up and responsive."""

    sftp_service = SourceFtp()

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(
            sftp_service,
            logger,
            config,
        ),
    )

    return sftp_service


@pytest.fixture(scope="session")
def sftp_service_pk(config_pk, docker_services):
    """Ensure that SFTP service is up and responsive."""

    sftp_service_pk = SourceFtp()

    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(
            sftp_service_pk,
            logger,
            config_pk,
        ),
    )

    return sftp_service_pk


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}},
    }

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="overwrite_stream",
            json_schema=stream_schema,
            supported_sync_modes=[
                SyncMode.full_refresh,
                SyncMode.incremental,
            ],
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[overwrite_stream])


def test_check_valid_config_pk(
    config_pk: Mapping,
    sftp_service_pk: SourceFtp,
):
    # actual test
    outcome = sftp_service_pk.check(logger, config_pk)
    assert outcome.status == Status.SUCCEEDED


def test_check_valid_config_pk_bad_pk(
    config_pk: Mapping,
    sftp_service_pk: SourceFtp,
):
    bad_config_pk = {
        **config_pk,
        "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----",
    }

    bad_outcome = sftp_service_pk.check(
        logger,
        bad_config_pk,
    )

    assert bad_outcome.status == Status.FAILED


def test_check_invalid_config(config: Mapping, sftp_service: SourceFtp):
    invalid_config = {**config, "password": "wrongpass"}
    outcome = sftp_service.check(logger, invalid_config)
    assert outcome.status == Status.FAILED


def test_check_valid_config(
    config: Mapping,
    sftp_service: SourceFtp,
):
    # actual test
    outcome = sftp_service.check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_get_files_no_pattern_json(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        config,
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_json(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "file_pattern": "test_1.+"},
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "foo"
        assert res.record.data["int_col"] == 2


def test_get_files_pattern_json_new_separator(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "file_pattern": "test_2.+"},
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "hello"
        assert res.record.data["int_col"] == 1


def test_get_files_pattern_no_match_json(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "file_pattern": "bad_pattern.+"},
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]
    assert len(result) == 0


def test_get_files_no_pattern_csv(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "file_type": "csv", "folder_path": "files/csv"},
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 4
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {
            **config,
            "file_type": "csv",
            "folder_path": "files/csv",
            "file_pattern": "test_1.+",
        },
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {
            **config,
            "file_type": "csv",
            "folder_path": "files/csv",
            "file_pattern": "test_2.+",
        },
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator_with_config(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {
            **config,
            "file_type": "csv",
            "folder_path": "files/csv",
            "separator": ";",
            "file_pattern": "test_2.+",
        },
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_no_match_csv(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {
            **config,
            "file_type": "csv",
            "folder_path": "files/csv",
            "file_pattern": "badpattern.+",
        },
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]
    assert len(result) == 0


def test_get_files_empty_files(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "folder_path": "files/json_empty"},
        configured_catalog,
        None,
    )

    result = [m for m in result_iter if m.type is Type.RECORD]
    assert len(result) == 0


def test_get_files_handle_null_values(
    config: Mapping,
    configured_catalog: ConfiguredAirbyteCatalog,
    sftp_service: SourceFtp,
):
    result_iter = sftp_service.read(
        logger,
        {**config, "folder_path": "files/csv_null_values", "file_type": "csv"},
        configured_catalog,
        None,
    )
    result = [m for m in result_iter if m.type is Type.RECORD]

    assert len(result) == 5

    res = result[2]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == "bar"
    assert res.record.data["int_col"] is None

    res = result[4]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] is None
    assert res.record.data["int_col"] == 4


def test_get_files_recusively_depth(
    docker_services,
):
    pass
