---
id: airbyte-validate
title: airbyte.validate
---

Module airbyte.validate
=======================
Defines the `airbyte-lib-validate-source` CLI.

This tool checks if connectors are compatible with PyAirbyte.

Functions
---------

`full_tests(connector_name: str, sample_config: str) ‑> None`
:   Run full tests on the connector.

`install_only_test(connector_name: str) ‑> None`
:   Test that the connector can be installed and spec can be printed.

`run() ‑> None`
:   Handle CLI entrypoint for the `airbyte-lib-validate-source` command.
    
    It's called like this:
    > airbyte-lib-validate-source —connector-dir . -—sample-config secrets/config.json
    
    It performs a basic smoke test to make sure the connector in question is PyAirbyte compliant:
    * Can be installed into a venv
    * Can be called via cli entrypoint
    * Answers according to the Airbyte protocol when called with spec, check, discover and read.

`validate(connector_dir: str, sample_config: str, *, validate_install_only: bool) ‑> None`
:   Validate a connector.