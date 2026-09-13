"""Root pytest configuration.

`pytest_plugins` must be declared here rather than in `integration_tests/`:
pytest only collects `pytest_addoption` hooks from the rootdir conftest, so the
CDK's `--connector-image` option is invisible when the plugin is declared
deeper in the tree.
"""

pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]
