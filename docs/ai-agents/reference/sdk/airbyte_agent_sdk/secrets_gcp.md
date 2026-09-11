---
id: airbyte_agent_sdk-secrets_gcp
title: airbyte_agent_sdk.secrets_gcp
---

Module airbyte_agent_sdk.secrets_gcp
====================================
GCP Secret Manager hydration for executable bundles (opt-in `secrets-gcp` extra).

This module is only reached on the opt-in local execution path -- when
`SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`, the SDK calls
`POST /connectors/{id}/execute/prepare` and resolves the returned bundle's
unhydrated `secret_coordinate::` values against the customer's own GCP Secret
Manager in their data plane. `google-cloud-secret-manager` is imported lazily
inside `hydrate_source_config` so the base install (without the
`secrets-gcp` extra) never imports it on the hosted path.

Provider selection lives in
`airbyte_agent_sdk.config.resolve_secret_manager_provider`: set
`SECRET_MANAGER_PROVIDER=gcp` to select this module explicitly. Absent that
variable, GCP is inferred when any of `GCP_SECRET_MANAGER_PROJECT_ID`,
`GCP_SECRET_MANAGER_CREDENTIALS_JSON`, or
`GCP_SECRET_MANAGER_CREDENTIALS_PATH` is set; otherwise AWS remains the
default.

Coordinate forms accepted after the `secret_coordinate::` prefix:

- A full resource name, `projects/<project>/secrets/<id>`, optionally already
  carrying `/versions/<version>`. Used as given; the configured version is
  appended when absent.
- A bare secret id such as `organization_<org_id>__source_config__<uuid>`,
  expanded to `projects/<project>/secrets/<id>/versions/<version>` using the
  resolved project. Legacy coordinates containing `/` are rewritten to `__`,
  since GCP Secret Manager secret ids cannot contain a slash.

Credentials come from `airbyte_agent_sdk.config.resolve_gcp_credentials`, which
reads those same `GCP_SECRET_MANAGER_*` variables and falls back to Application
Default Credentials; when no project is configured explicitly, the project
discovered alongside the credentials is used. Each distinct coordinate is
fetched once per hydration call, and hydration fails closed -- a credential or
fetch failure raises rather than falling back to hosted execution.

Stored values must be plaintext UTF-8 scalars; a JSON object or array payload is
rejected rather than injected into the connector config, matching
`airbyte_agent_sdk.secrets_aws`.

Functions
---------

<a id="hydrate_source_config"></a>

`hydrate_source_config(source_config: dict[str, Any], *, credentials: GCPDataPlaneCredentials | None = None) ‑> dict[str, typing.Any]`
:   Resolve `secret_coordinate::` values in *source_config* via GCP Secret Manager.
    
    Walks nested dicts/lists and returns a fully hydrated copy of the config.
    
    Raises:
        ImportError: If google-cloud-secret-manager is not installed (missing
            `secrets-gcp` extra).
        ValueError: If credentials are misconfigured, no project can be resolved
            for a bare coordinate, or a coordinate does not resolve to a
            plaintext UTF-8 value.