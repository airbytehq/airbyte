---
id: airbyte_agent_sdk-secrets_aws
title: airbyte_agent_sdk.secrets_aws
---

Module airbyte_agent_sdk.secrets_aws
====================================
AWS Secrets Manager hydration for executable bundles (opt-in `secrets-aws` extra).

This module is only reached on the opt-in local execution path -- when
`SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`, the SDK calls
`POST /connectors/{id}/execute/prepare` and resolves the returned bundle's
unhydrated `secret_coordinate::` values against the customer's own AWS Secrets
Manager in their data plane. `boto3` is imported lazily inside
`hydrate_source_config` so the base install (without the `secrets-aws`
extra) never imports boto3 on the hosted path.

Functions
---------

<a id="hydrate_source_config"></a>

`hydrate_source_config(source_config: dict[str, Any], *, credentials: AWSDataPlaneCredentials | None = None) ‑> dict[str, typing.Any]`
:   Resolve `secret_coordinate::` values in *source_config* via AWS Secrets Manager.
    
    Walks nested dicts/lists and replaces every `secret_coordinate::<id>` string
    with the secret value fetched from AWS Secrets Manager, returning a fully
    hydrated config. Fails closed: any credential or fetch failure raises rather
    than falling back to hosted execution.
    
    Raises:
        ImportError: If boto3 is not installed (missing `secrets-aws` extra).
        ValueError: If AWS credentials are absent or a coordinate cannot be resolved.