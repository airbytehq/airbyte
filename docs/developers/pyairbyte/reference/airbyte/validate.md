---
sidebar_label: validate
title: airbyte.validate
---

Defines the `airbyte-lib-validate-source` CLI.

This tool checks if connectors are compatible with PyAirbyte.

## annotations

## argparse

## json

## os

## subprocess

## sys

## tempfile

## Path

## yaml

## print

## ab

## exc

## get\_bin\_dir

## NO\_UV

#### \_parse\_args

```python
def _parse_args() -> argparse.Namespace
```

#### \_run\_subprocess\_and\_raise\_on\_failure

```python
def _run_subprocess_and_raise_on_failure(args: list[str]) -> None
```

#### full\_tests

```python
def full_tests(connector_name: str, sample_config: str) -> None
```

Run full tests on the connector.

#### install\_only\_test

```python
def install_only_test(connector_name: str) -> None
```

Test that the connector can be installed and spec can be printed.

#### run

```python
def run() -> None
```

Handle CLI entrypoint for the `airbyte-lib-validate-source` command.

It&#x27;s called like this:
&gt; airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json

It performs a basic smoke test to make sure the connector in question is PyAirbyte compliant:
* Can be installed into a venv
* Can be called via cli entrypoint
* Answers according to the Airbyte protocol when called with spec, check, discover and read.

#### validate

```python
def validate(connector_dir: str, sample_config: str, *,
             validate_install_only: bool) -> None
```

Validate a connector.

