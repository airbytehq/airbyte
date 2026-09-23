import pytest
from hdbcli import dbapi

from source_sap_hana.client import HanaClient, is_retryable, qualified_name
from source_sap_hana.config import HanaConfig, StreamSettings, parse_connection_properties, parse_stream_settings


def test_parse_connection_properties():
    assert parse_connection_properties(" communicationTimeout=0 ; reconnect=TRUE;") == {
        "communicationTimeout": "0",
        "reconnect": "TRUE",
    }
    assert parse_connection_properties(None) == {}
    with pytest.raises(ValueError):
        parse_connection_properties("novalue")


def test_connect_kwargs(config, logger):
    config.update(
        database_name="S4P",
        encrypt=True,
        ssl_validate_certificate=False,
        connection_properties="communicationTimeout=0",
    )
    kwargs = HanaClient(HanaConfig.from_mapping(config), logger).connect_kwargs()
    assert kwargs == {
        "address": "hana.example.com",
        "port": 30015,
        "user": "AIRBYTE",
        "password": "secret",
        "databaseName": "S4P",
        "compress": True,
        "encrypt": True,
        "sslValidateCertificate": False,
        "communicationTimeout": "0",
    }


def test_no_tls_kwargs_when_encryption_disabled(config, logger):
    kwargs = HanaClient(HanaConfig.from_mapping(config), logger).connect_kwargs()
    assert "encrypt" not in kwargs and "sslValidateCertificate" not in kwargs


def test_compression_can_be_disabled(config, logger):
    config["compress"] = False
    assert "compress" not in HanaClient(HanaConfig.from_mapping(config), logger).connect_kwargs()


def test_is_retryable():
    assert is_retryable(dbapi.OperationalError(-10807, "Connection down"))
    assert is_retryable(dbapi.Error(-10709, "Connection failed"))
    assert not is_retryable(dbapi.Error(10, "authentication failed"))
    assert not is_retryable(dbapi.ProgrammingError(259, "invalid table name"))
    assert not is_retryable(ValueError("boom"))


def test_qualified_name_quotes_sap_namespaces():
    assert qualified_name("SAPHANADB", "/BIC/AZSALES00") == '"SAPHANADB"."/BIC/AZSALES00"'
    assert qualified_name("S", 'A"B') == '"S"."A""B"'


def test_parse_stream_settings():
    settings = parse_stream_settings(
        [
            {"stream": "ACDOCA", "condition": "RCLNT = '100'", "cursor_field": "TIMESTAMP", "primary_key": ["RCLNT", " BELNR "]},
            {"stream": "SAPHANADB.MARA", "condition": " MTART <> 'ZROY' "},
        ]
    )
    assert settings == {
        (None, "ACDOCA"): StreamSettings(condition="RCLNT = '100'", cursor_field="TIMESTAMP", primary_key=("RCLNT", "BELNR")),
        ("SAPHANADB", "MARA"): StreamSettings(condition="MTART <> 'ZROY'"),
    }


@pytest.mark.parametrize(
    "raw",
    [
        [{"stream": "ACDOCA"}],
        [{"stream": "", "condition": "1=1"}],
        [{"stream": "ACDOCA", "condition": "1=1; DROP TABLE X"}],
        [{"stream": "ACDOCA", "condition": "1=1"}, {"stream": "ACDOCA", "condition": "2=2"}],
    ],
)
def test_parse_stream_settings_rejects_invalid(raw):
    with pytest.raises(ValueError):
        parse_stream_settings(raw)


def test_schema_qualified_settings_win(config):
    config["stream_settings"] = [
        {"stream": "ACDOCA", "condition": "generic"},
        {"stream": "SAPHANADB.ACDOCA", "condition": "specific"},
    ]
    cfg = HanaConfig.from_mapping(config)
    assert cfg.stream_filter("SAPHANADB", "ACDOCA") == "specific"
    assert cfg.stream_filter("OTHER", "ACDOCA") == "generic"
    assert cfg.stream_filter("SAPHANADB", "MARA") is None
