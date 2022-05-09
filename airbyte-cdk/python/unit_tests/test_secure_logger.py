#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from argparse import Namespace
from typing import Any, Iterable, Mapping, MutableMapping

import pytest
from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Type
from airbyte_cdk.sources import Source

SECRET_PROPERTY = "api_token"
ANOTHER_SECRET_PROPERTY = "another_api_token"
ANOTHER_NOT_SECRET_PROPERTY = "not_secret_property"

NOT_SECRET_PROPERTY = "explicitly_not_secret_property"

I_AM_A_SECRET_VALUE = "I am a secret"
ANOTHER_SECRET_VALUE = "Another secret"
SECRET_INTEGER_VALUE = 123456789
NOT_A_SECRET_VALUE = "I am not a secret"
ANOTHER_NOT_SECRET_VALUE = "I am not a secret"


class MockSource(Source):
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterable[AirbyteMessage]:
        logger.info(I_AM_A_SECRET_VALUE)
        logger.info(I_AM_A_SECRET_VALUE + " plus Some non secret Value in the same log record" + NOT_A_SECRET_VALUE)
        logger.info(NOT_A_SECRET_VALUE)
        yield AirbyteMessage(
            record=AirbyteRecordMessage(stream="stream", data={"data": "stuff"}, emitted_at=1),
            type=Type.RECORD,
        )

    def discover(self, **kwargs):
        pass

    def check(self, **kwargs):
        pass


spec_with_airbyte_secrets = {
    "type": "object",
    "required": ["api_token"],
    "additionalProperties": False,
    "properties": {
        SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
        NOT_SECRET_PROPERTY: {"type": "string", "airbyte_secret": False},
    },
}

spec_with_airbyte_secrets_config = {
    SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
    NOT_SECRET_PROPERTY: NOT_A_SECRET_VALUE,
}

spec_with_multiple_airbyte_secrets = {
    "type": "object",
    "required": ["api_token"],
    "additionalProperties": True,
    "properties": {
        SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
        ANOTHER_SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
        NOT_SECRET_PROPERTY: {"type": "string", "airbyte_secret": False},
        ANOTHER_NOT_SECRET_PROPERTY: {"type": "string"},
    },
}

spec_with_multiple_airbyte_secrets_config = {
    SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
    NOT_SECRET_PROPERTY: NOT_A_SECRET_VALUE,
    ANOTHER_SECRET_PROPERTY: ANOTHER_SECRET_VALUE,
    ANOTHER_NOT_SECRET_PROPERTY: ANOTHER_NOT_SECRET_VALUE,
}

spec_with_airbyte_secrets_not_string = {
    "type": "object",
    "required": ["api_token"],
    "additionalProperties": True,
    "properties": {
        SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
        ANOTHER_SECRET_PROPERTY: {"type": "integer", "airbyte_secret": True},
    },
}

spec_with_airbyte_secrets_not_string_config = {
    SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
    ANOTHER_SECRET_PROPERTY: SECRET_INTEGER_VALUE,
}


@pytest.fixture
def simple_config():
    yield {
        SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
        ANOTHER_SECRET_PROPERTY: ANOTHER_SECRET_VALUE,
    }


@pytest.mark.parametrize(
    "source_spec, config",
    [
        [spec_with_airbyte_secrets, spec_with_airbyte_secrets_config],
        [spec_with_multiple_airbyte_secrets, spec_with_multiple_airbyte_secrets_config],
        [
            spec_with_airbyte_secrets_not_string,
            spec_with_airbyte_secrets_not_string_config,
        ],
    ],
    ids=[
        "spec_with_airbyte_secrets",
        "spec_with_multiple_airbyte_secrets",
        "spec_with_airbyte_secrets_not_string",
    ],
)
def test_airbyte_secret_is_masked_on_logger_output(source_spec, mocker, config, caplog):
    caplog.set_level(logging.DEBUG, logger="airbyte.test")
    caplog.handler.setFormatter(AirbyteLogFormatter())
    entrypoint = AirbyteEntrypoint(MockSource())
    parsed_args = Namespace(command="read", config="", state="", catalog="")
    mocker.patch.object(
        MockSource,
        "spec",
        return_value=ConnectorSpecification(connectionSpecification=source_spec),
    )
    mocker.patch.object(MockSource, "configure", return_value=config)
    mocker.patch.object(MockSource, "read_config", return_value=None)
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})
    list(entrypoint.run(parsed_args))
    log_result = caplog.text
    expected_secret_values = [config[k] for k, v in source_spec["properties"].items() if v.get("airbyte_secret")]
    expected_plain_text_values = [config[k] for k, v in source_spec["properties"].items() if not v.get("airbyte_secret")]
    assert all([str(v) not in log_result for v in expected_secret_values])
    assert all([str(v) in log_result for v in expected_plain_text_values])


def test_airbyte_secrets_are_masked_on_uncaught_exceptions(mocker, caplog, capsys):
    caplog.set_level(logging.DEBUG, logger="airbyte.test")
    caplog.handler.setFormatter(AirbyteLogFormatter())

    class BrokenSource(MockSource):
        def read(
            self,
            logger: logging.Logger,
            config: Mapping[str, Any],
            catalog: ConfiguredAirbyteCatalog,
            state: MutableMapping[str, Any] = None,
        ):
            raise Exception("Exception:" + I_AM_A_SECRET_VALUE)

    entrypoint = AirbyteEntrypoint(BrokenSource())
    parsed_args = Namespace(command="read", config="", state="", catalog="")
    source_spec = {
        "type": "object",
        "required": ["api_token"],
        "additionalProperties": False,
        "properties": {
            SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
            NOT_SECRET_PROPERTY: {"type": "string", "airbyte_secret": False},
        },
    }
    simple_config = {
        SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
        NOT_SECRET_PROPERTY: NOT_A_SECRET_VALUE,
    }
    mocker.patch.object(
        MockSource,
        "spec",
        return_value=ConnectorSpecification(connectionSpecification=source_spec),
    )
    mocker.patch.object(MockSource, "configure", return_value=simple_config)
    mocker.patch.object(MockSource, "read_config", return_value=None)
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})

    try:
        list(entrypoint.run(parsed_args))
    except Exception:
        sys.excepthook(*sys.exc_info())
        assert I_AM_A_SECRET_VALUE not in capsys.readouterr().out, "Should have filtered non-secret value from exception trace message"
        assert I_AM_A_SECRET_VALUE not in caplog.text, "Should have filtered secret value from exception log message"


def test_non_airbyte_secrets_are_not_masked_on_uncaught_exceptions(mocker, caplog, capsys):
    caplog.set_level(logging.DEBUG, logger="airbyte.test")
    caplog.handler.setFormatter(AirbyteLogFormatter())

    class BrokenSource(MockSource):
        def read(
            self,
            logger: logging.Logger,
            config: Mapping[str, Any],
            catalog: ConfiguredAirbyteCatalog,
            state: MutableMapping[str, Any] = None,
        ):
            raise Exception("Exception:" + NOT_A_SECRET_VALUE)

    entrypoint = AirbyteEntrypoint(BrokenSource())
    parsed_args = Namespace(command="read", config="", state="", catalog="")
    source_spec = {
        "type": "object",
        "required": ["api_token"],
        "additionalProperties": False,
        "properties": {
            SECRET_PROPERTY: {"type": "string", "airbyte_secret": True},
            NOT_SECRET_PROPERTY: {"type": "string", "airbyte_secret": False},
        },
    }
    simple_config = {
        SECRET_PROPERTY: I_AM_A_SECRET_VALUE,
        NOT_SECRET_PROPERTY: NOT_A_SECRET_VALUE,
    }
    mocker.patch.object(
        MockSource,
        "spec",
        return_value=ConnectorSpecification(connectionSpecification=source_spec),
    )
    mocker.patch.object(MockSource, "configure", return_value=simple_config)
    mocker.patch.object(MockSource, "read_config", return_value=None)
    mocker.patch.object(MockSource, "read_state", return_value={})
    mocker.patch.object(MockSource, "read_catalog", return_value={})
    mocker.patch.object(MockSource, "read", side_effect=Exception("Exception:" + NOT_A_SECRET_VALUE))

    try:
        list(entrypoint.run(parsed_args))
    except Exception:
        sys.excepthook(*sys.exc_info())
        assert NOT_A_SECRET_VALUE in capsys.readouterr().out, "Should not have filtered non-secret value from exception trace message"
        assert NOT_A_SECRET_VALUE in caplog.text, "Should not have filtered non-secret value from exception log message"
