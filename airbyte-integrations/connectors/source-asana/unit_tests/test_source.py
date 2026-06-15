#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_asana.source import SourceAsana


def test_oauth_connector_input_specification_includes_default_scope():
    source = SourceAsana(catalog=None, config=None, state=None)

    spec = source.spec(None)
    oauth_spec = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert oauth_spec.scopes == [{"scope": "default"}]
