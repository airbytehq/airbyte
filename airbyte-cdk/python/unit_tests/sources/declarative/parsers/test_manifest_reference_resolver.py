#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver

resolver = ManifestReferenceResolver()


def test_get_ref():
    s = """
    limit_ref: "*ref(limit)"
    """
    ref_key = resolver._get_ref_key(s)
    assert ref_key == "limit"


def test_get_ref_no_ref():
    s = """
    limit: 50
    """
    ref_key = resolver._get_ref_key(s)
    assert ref_key is None
