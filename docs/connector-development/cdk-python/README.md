# Connector Development Kit (Python)

The Airbyte Python CDK is a framework for rapidly developing production-grade Airbyte connectors. The CDK currently offers helpers specific for creating Airbyte source connectors for:

* HTTP APIs \(REST APIs, GraphQL, etc..\)
* Generic Python sources \(anything not covered by the above\)
* Singer Taps (Note: The CDK supports building Singer taps but Airbyte no longer access contributions of this type)

The CDK provides an improved developer experience by providing basic implementation structure and abstracting away low-level glue boilerplate.

This document is a general introduction to the CDK. Readers should have basic familiarity with the [Airbyte Specification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/) before proceeding.

If you have any issues with troubleshooting or want to learn more about the CDK from the Airbyte team, head to [the Connector Development section of our Discourse forum](https://discuss.airbyte.io/c/connector-development/16) to inquire further!

## Getting Started

Generate an empty connector using the code generator. First clone the Airbyte repository then from the repository root run

```text
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

then follow the interactive prompt. Next, find all `TODO`s in the generated project directory -- they're accompanied by lots of comments explaining what you'll need to do in order to implement your connector. Upon completing all TODOs properly, you should have a functioning connector.

Additionally, you can follow [this tutorial](../tutorials/cdk-tutorial-python-http/getting-started.md) for a complete walkthrough of creating an HTTP connector using the Airbyte CDK.

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

You can find a complete tutorial for implementing an HTTP source connector in [this tutorial](../tutorials/cdk-tutorial-python-http/getting-started.md)

### Example Connectors

**HTTP Connectors**:

* [Exchangerates API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py)
* [Stripe](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py)
* [Slack](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py)

**Simple Python connectors using the barebones `Source` abstraction**:

* [Google Sheets](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-google-sheets/google_sheets_source/google_sheets_source.py)
* [Mailchimp](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mailchimp/source_mailchimp/source.py)

## Contributing

### First time setup

We assume `python` points to python &gt;=3.9.

Setup a virtual env:

```text
python -m venv .venv
source .venv/bin/activate
pip install -e ".[tests]" # [tests] installs test-only dependencies
```

#### Iteration

* Iterate on the code locally
* Run tests via `pytest -s unit_tests`
* Perform static type checks using `mypy airbyte_cdk`. `MyPy` configuration is in `.mypy.ini`.
* The `type_check_and_test.sh` script bundles both type checking and testing in one convenient command. Feel free to use it!

#### Debugging

While developing your connector, you can print detailed debug information during a sync by specifying the `--debug` flag. This allows you to get a better picture of what is happening during each step of your sync.
```text
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

## Coming Soon

* Full OAuth 2.0 support \(including refresh token issuing flow via UI or CLI\) 
* Airbyte Java HTTP CDK
* CDK for Async HTTP endpoints \(request-poll-wait style endpoints\)
* CDK for other protocols
* Don't see a feature you need? [Create an issue and let us know how we can help!](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement&template=feature-request.md&title=)

