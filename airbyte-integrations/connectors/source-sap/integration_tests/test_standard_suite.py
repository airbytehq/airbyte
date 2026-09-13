"""Airbyte's standard connector tests, driven from acceptance-test-config.yml.

Run them against an image we built ourselves:

    ./bin/build-image.sh
    uv run pytest integration_tests --connector-image datazoo/source-sap:dev

Without `--connector-image` the CDK generates its own Poetry-based Dockerfile,
which cannot bake in the ERPL extensions this connector loads, so the
docker-image cases are expected to fail in that mode.
"""

import pytest

standard_tests = pytest.importorskip("airbyte_cdk.test.standard_tests")


class TestSuiteSourceSap(standard_tests.SourceTestSuiteBase):
    """Standard spec / check / discover / read coverage."""
