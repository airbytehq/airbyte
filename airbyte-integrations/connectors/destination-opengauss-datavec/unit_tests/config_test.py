#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_opengauss_datavec.config import (
    ConfigModel,
    OpenGaussDataVecIndexingModel,
    PasswordBasedAuthorizationModel,
    SslModeVerifyCa,
)
from pydantic import ValidationError


def indexing_config(**overrides):
    config = {
        "host": "localhost",
        "database": "db",
        "username": "user",
        "credentials": {"password": "password"},
    }
    config.update(overrides)
    return config


def test_indexing_config_applies_defaults():
    config = OpenGaussDataVecIndexingModel.parse_obj(indexing_config())

    assert config.port == 5432
    assert config.default_schema == "public"
    assert config.ssl_mode.mode == "disable"
    assert config.credentials.password == "password"


def test_indexing_config_accepts_verify_ca_ssl_mode():
    config = OpenGaussDataVecIndexingModel.parse_obj(indexing_config(ssl_mode={"mode": "verify-ca", "ca_certificate": "certificate"}))

    assert isinstance(config.ssl_mode, SslModeVerifyCa)
    assert config.ssl_mode.ca_certificate == "certificate"


def test_indexing_config_rejects_verify_ca_without_certificate():
    with pytest.raises(ValidationError):
        OpenGaussDataVecIndexingModel.parse_obj(indexing_config(ssl_mode={"mode": "verify-ca"}))


def test_config_model_preserves_omit_raw_text_and_nested_indexing():
    config = ConfigModel.parse_obj(
        {
            "processing": {"text_fields": ["body"], "metadata_fields": ["id"], "chunk_size": 1000},
            "embedding": {"mode": "fake"},
            "indexing": indexing_config(default_schema="analytics"),
            "omit_raw_text": True,
        }
    )

    assert config.omit_raw_text is True
    assert config.indexing.default_schema == "analytics"
    assert config.processing.metadata_fields == ["id"]


def test_password_model_marks_password_as_secret_in_schema():
    schema = PasswordBasedAuthorizationModel.schema()

    assert schema["properties"]["password"]["airbyte_secret"] is True
