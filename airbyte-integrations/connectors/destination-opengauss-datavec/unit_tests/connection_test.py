#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import MagicMock, patch

from destination_opengauss_datavec.config import OpenGaussDataVecIndexingModel, PasswordBasedAuthorizationModel
from destination_opengauss_datavec.connection import OpenGaussSslConnectionOptions, get_connection


def indexing_config(ssl_mode):
    return OpenGaussDataVecIndexingModel(
        host="localhost",
        port=5432,
        database="db",
        default_schema="public",
        username="user",
        ssl_mode=ssl_mode,
        credentials=PasswordBasedAuthorizationModel(password="password"),
    )


def test_ssl_connection_options_pass_through_simple_modes():
    for mode in ["disable", "allow", "prefer", "require"]:
        options = OpenGaussSslConnectionOptions(indexing_config({"mode": mode}))

        assert options.build() == {"sslmode": mode}


def test_ssl_connection_options_writes_verify_ca_certificate():
    ca_certificate = "-----BEGIN CERTIFICATE-----\ntest-ca\n-----END CERTIFICATE-----"
    options = OpenGaussSslConnectionOptions(indexing_config({"mode": "verify-ca", "ca_certificate": ca_certificate}))

    connection_options = options.build()

    assert connection_options["sslmode"] == "verify-ca"
    sslrootcert = Path(connection_options["sslrootcert"])
    assert sslrootcert.name == "ca.crt"
    assert sslrootcert.read_text(encoding="utf-8") == ca_certificate


def test_ssl_connection_options_reuses_certificate_directory():
    options = OpenGaussSslConnectionOptions(indexing_config({"mode": "verify-ca", "ca_certificate": "first"}))

    first_options = options.build()
    options.config.ssl_mode.ca_certificate = "second"
    second_options = options.build()

    assert Path(first_options["sslrootcert"]).parent == Path(second_options["sslrootcert"]).parent
    assert Path(second_options["sslrootcert"]).read_text(encoding="utf-8") == "second"


def test_get_connection_passes_database_credentials_and_ssl_options():
    config = indexing_config({"mode": "require"})
    connection = MagicMock()
    connection.__enter__.return_value = connection
    ssl_options = OpenGaussSslConnectionOptions(config)

    with patch("destination_opengauss_datavec.connection.psycopg2.connect", return_value=connection) as connect:
        returned_connection = get_connection(config, ssl_options)
        assert returned_connection is connection

    connect.assert_called_once_with(
        host="localhost",
        port=5432,
        dbname="db",
        user="user",
        password="password",
        connect_timeout=20,
        keepalives=1,
        keepalives_idle=60,
        keepalives_interval=10,
        keepalives_count=5,
        sslmode="require",
    )
