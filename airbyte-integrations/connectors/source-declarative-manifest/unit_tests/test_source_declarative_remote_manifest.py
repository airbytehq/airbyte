#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from source_declarative_manifest.run import create_manifest, handle_command

REMOTE_MANIFEST_SPEC_SUBSTRING = '"required":["__injected_declarative_manifest"]'


def test_spec_does_not_raise_value_error(capsys):
    handle_command(["spec"])
    stdout = capsys.readouterr()
    assert REMOTE_MANIFEST_SPEC_SUBSTRING in stdout.out


def test_given_no_injected_declarative_manifest_then_raise_value_error(invalid_remote_config):
    with pytest.raises(ValueError):
        create_manifest(["check", "--config", str(invalid_remote_config)])


def test_given_injected_declarative_manifest_then_return_declarative_manifest(valid_remote_config):
    source = create_manifest(["check", "--config", str(valid_remote_config)])
    assert isinstance(source, ManifestDeclarativeSource)
