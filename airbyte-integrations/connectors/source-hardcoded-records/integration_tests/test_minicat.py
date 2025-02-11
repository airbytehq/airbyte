"""Mini-CAT test for Google Sheets source.

We import the `MiniCAT` class from the CDK. This gives us the ability to step-debug tests and
iterate locally and quickly.
"""

from airbyte_cdk.test import SourceTestSuiteBase


class MyMiniCAT(SourceTestSuiteBase):
    """Instantiates the Mini-CAT test suite for Google Sheets source.

    This suite can be run with pytest. All config is optional.
    """
