#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
import tempfile
import unittest

from airbyte_cdk.sources.declarative.exceptions import InvalidConnectorDefinitionException
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class TestYamlDeclarativeSource(unittest.TestCase):
    def test_source_is_created_if_toplevel_fields_are_known(self):
        content = """
        version: "version"
        streams: "streams"
        check: "check"
        """
        temporary_file = TestFileContent(content)
        YamlDeclarativeSource(temporary_file.filename)

    def test_source_is_not_created_if_toplevel_fields_are_unknown(self):
        content = """
        version: "version"
        streams: "streams"
        check: "check"
        not_a_valid_field: "error"
        """
        temporary_file = TestFileContent(content)
        with self.assertRaises(InvalidConnectorDefinitionException):
            YamlDeclarativeSource(temporary_file.filename)


class TestFileContent:
    def __init__(self, content):
        self.file = tempfile.NamedTemporaryFile(mode="w", delete=False)

        with self.file as f:
            f.write(content)

    @property
    def filename(self):
        return self.file.name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.unlink(self.filename)
