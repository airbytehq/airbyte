# Connector Development Kit

:::info
Over the next few months, the project will only accept connector contributions that are made using the
[Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview) or the
[Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview).

New pull requests made with the Python CDK will be closed, but we will inquire to understand why it wasn't done with
Low-Code/Connector Builder so we can address missing features. This decision is aimed at improving maintenance and
providing a larger catalog with high-quality connectors.

You can continue to use the Python CDK to build connectors to help your company or projects.
:::

:::info
Developer updates will be announced via
[#help-connector-development](https://airbytehq.slack.com/archives/C027KKE4BCZ) Slack channel. If you are using the
CDK, please join to stay up to date on changes and issues.
:::

:::info
This section is for the Python CDK. See our
[community-maintained CDKs section](../README.md#community-maintained-cdks) if you want to write connectors in other
languages.
:::

The Airbyte Python CDK is a framework for rapidly developing production-grade Airbyte connectors. The CDK currently
offers helpers specific for creating Airbyte source connectors for:

- HTTP APIs \(REST APIs, GraphQL, etc..\)
- Generic Python sources \(anything not covered by the above\)

This document is a general introduction to the CDK. Readers should have basic familiarity with the
[Airbyte Specification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/) before proceeding.

If you have any issues with troubleshooting or want to learn more about the CDK from the Airbyte team, head to
[the Connector Development section of our Airbyte Forum](https://github.com/airbytehq/airbyte/discussions) to
inquire further!

## Getting Started

Generate an empty connector using the code generator. First clone the Airbyte repository, then from the repository
root run

```bash
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

Next, find all `TODO`s in the generated project directory. They're accompanied by comments explaining what you'll
need to do in order to implement your connector. Upon completing all TODOs properly, you should have a functioning connector.

Additionally, you can follow [this tutorial](../tutorials/custom-python-connector/0-getting-started.md) for a complete walkthrough of creating an HTTP connector using the Airbyte CDK.

### Concepts & Documentation

#### Basic Concepts

If you want to learn more about the classes required to implement an Airbyte Source, head to our [basic concepts doc](basic-concepts.md).

#### Full Refresh Streams

If you have questions or are running into issues creating your first full refresh stream, head over to our [full refresh stream doc](full-refresh-stream.md). If you have questions about implementing a `path` or `parse_response` function, this doc is for you.

#### Incremental Streams

Having trouble figuring out how to write a `stream_slices` function or aren't sure what a `cursor_field` is? Head to our [incremental stream doc](incremental-stream.md).

#### Practical Tips

Airbyte recommends using the CDK template generator to develop with the CDK. The template generates created all the required scaffolding, with convenient TODOs, allowing developers to truly focus on implementing the API.

For tips on useful Python knowledge, see the [Python Concepts](python-concepts.md) page.

You can find a complete tutorial for implementing an HTTP source connector in [this tutorial](../tutorials/custom-python-connector/0-getting-started.md)

### Example Connectors

**HTTP Connectors**:

- [Stripe](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py)
- [Slack](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py)

**Simple Python connectors using the barebones `Source` abstraction**:

- [Google Sheets](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-google-sheets/source_google_sheets/source.py)
- [Mailchimp](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mailchimp/source_mailchimp/source.py)

## Contributing

### First time setup

We assume `python` points to Python 3.9 or higher.

Setup a virtual env:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[tests]" # [tests] installs test-only dependencies
```

#### Iteration

- Iterate on the code locally
- Run tests via `pytest -s unit_tests`
- Perform static type checks using `mypy airbyte_cdk`. `MyPy` configuration is in `.mypy.ini`.
- The `type_check_and_test.sh` script bundles both type checking and testing in one convenient command. Feel free to use it!

#### Debugging

While developing your connector, you can print detailed debug information during a sync by specifying the `--debug` flag. This allows you to get a better picture of what is happening during each step of your sync.

```bash
python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json --debug
```

In addition to preset CDK debug statements, you can also add your own statements to emit debug information specific to your connector:

```python
self.logger.debug("your debug message here", extra={"debug_field": self.value})
```

#### Testing

All tests are located in the `unit_tests` directory. Run `pytest --cov=airbyte_cdk unit_tests/` to run them. This also presents a test coverage report.

#### Publishing a new version to PyPi

1. Open a PR
2. Once it is approved and merge, an Airbyte member must run the `Publish CDK Manually` workflow using `release-type=major|manor|patch` and setting the changelog message.
