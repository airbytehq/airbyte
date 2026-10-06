# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


from source_google_drive import SourceGoogleDrive

from airbyte_cdk.models import ConnectorSpecification


def test_source_instantiation():
    source = SourceGoogleDrive(catalog=None, config=None, state=None)
    assert isinstance(source, SourceGoogleDrive)


def test_source_spec():
    source = SourceGoogleDrive(catalog=None, config=None, state=None)
    spec = source.spec()
    assert isinstance(spec, ConnectorSpecification)
    assert spec.documentationUrl == "https://docs.airbyte.com/integrations/sources/google-drive"
