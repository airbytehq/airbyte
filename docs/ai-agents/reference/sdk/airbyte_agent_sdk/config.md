---
id: airbyte_agent_sdk-config
title: airbyte_agent_sdk.config
---

Module airbyte_agent_sdk.config
===============================
Global SDK configuration for Airbyte credentials.

Functions
---------

<a id="configure"></a>

`configure(*, client_id: str, client_secret: str, organization_id: str | None = None, workspace_name: str = 'default') ‑> None`
:   Set global SDK credentials. These are used as defaults by connect() and Workspace.
    
    Calling configure() again overwrites the previous configuration.
    Explicit kwargs passed to connect()/Workspace() always take priority.

<a id="get_config"></a>

`get_config() ‑> airbyte_agent_sdk.config.SDKConfig | None`
:   

<a id="resolve_aws_credentials"></a>

`resolve_aws_credentials(*, access_key_id: str | None = None, secret_access_key: str | None = None, session_token: str | None = None, region_name: str | None = None) ‑> airbyte_agent_sdk.config.AWSDataPlaneCredentials`
:   Resolve AWS data-plane credentials: explicit arg -> env var.
    
    Prefer the enterprise-flex secret-manager convention, then fall back to the
    standard AWS SDK environment variables. When no explicit keys are resolved,
    the returned credentials allow boto3 to source an implicit IAM role. Only
    consulted when `SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`.

<a id="resolve_credentials"></a>

`resolve_credentials(*, client_id: str | None = None, client_secret: str | None = None, organization_id: str | None = None, workspace_name: str | None = None) ‑> tuple[str, str, str | None, str]`
:   Resolve credentials: explicit arg -> global config -> env var.
    
    Returns (client_id, client_secret, organization_id, workspace_name).
    Raises ValueError if client_id or client_secret cannot be resolved.

<a id="resolve_gcp_credentials"></a>

`resolve_gcp_credentials(*, project_id: str | None = None, credentials_json: str | None = None, credentials_path: str | None = None, secret_version: str | None = None) ‑> airbyte_agent_sdk.config.GCPDataPlaneCredentials`
:   Resolve GCP Secret Manager credentials: explicit arg -> env var.
    
    See `GCPDataPlaneCredentials` for the environment variables consulted
    per field. Supplying both inline credentials JSON and a credentials path
    raises, since the effective identity would be ambiguous. When neither is
    supplied, the Google client library falls back to Application Default
    Credentials.

<a id="resolve_secret_manager_provider"></a>

`resolve_secret_manager_provider(provider: str | None = None) ‑> Literal['aws', 'gcp']`
:   Resolve which customer-owned secret manager should hydrate bundles.
    
    Consulted only on the local hydration path, which is enabled by
    `SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`. Precedence:
    
    1. The explicit *provider* argument, then `SECRET_MANAGER_PROVIDER`
       (`aws` or `gcp`); any other value raises.
    2. `gcp` when any of `GCP_SECRET_MANAGER_PROJECT_ID`,
       `GCP_SECRET_MANAGER_CREDENTIALS_JSON`, or
       `GCP_SECRET_MANAGER_CREDENTIALS_PATH` is set. The generic
       `GOOGLE_APPLICATION_CREDENTIALS` / `GOOGLE_CLOUD_PROJECT` variables
       are deliberately excluded here so an unrelated Google credential in the
       environment cannot switch providers.
    3. `aws` otherwise.

Classes
-------

<a id="AWSDataPlaneCredentials"></a>

`AWSDataPlaneCredentials(access_key_id: str | None = None, secret_access_key: str | None = None, session_token: str | None = None, region_name: str | None = None)`
:   AWS credentials for the customer's data plane.
    
    Consulted only on the local hydration path, which is enabled by
    `SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`. Any field may be `None`:
    when explicit keys are absent, boto3 falls back to its default provider
    chain (e.g. an implicit IAM role).

    ### Instance variables

    `access_key_id: str | None`
    :   The type of the None singleton.

    `has_explicit_keys: bool`
    :

    `region_name: str | None`
    :   The type of the None singleton.

    `secret_access_key: str | None`
    :   The type of the None singleton.

    `session_token: str | None`
    :   The type of the None singleton.

<a id="GCPDataPlaneCredentials"></a>

`GCPDataPlaneCredentials(project_id: str | None = None, credentials_json: str | None = None, credentials_path: str | None = None, secret_version: str = 'latest')`
:   GCP credentials for the customer's data plane.
    
    Consulted only on the local hydration path, which is enabled by
    `SECRETS_CONFIGURED_FROM_ENVIRONMENT=true`. If explicit credentials are
    absent, the Google client library falls back to Application Default
    Credentials.
    
    Fields, and the environment variables `resolve_gcp_credentials` reads
    for each:
    
    - `project_id` -- `GCP_SECRET_MANAGER_PROJECT_ID`, then
      `GOOGLE_CLOUD_PROJECT`, then `GCLOUD_PROJECT`. Needed only for bare
      (non `projects/...`) secret coordinates, and otherwise inferred from the
      resolved credentials.
    - `credentials_json` -- `GCP_SECRET_MANAGER_CREDENTIALS_JSON`, inline
      service-account JSON.
    - `credentials_path` -- `GCP_SECRET_MANAGER_CREDENTIALS_PATH`, then
      `GOOGLE_APPLICATION_CREDENTIALS`. Mutually exclusive with
      `credentials_json`.
    - `secret_version` -- `GCP_SECRET_MANAGER_SECRET_VERSION`, defaulting to
      `latest`.

    ### Instance variables

    `credentials_json: str | None`
    :   The type of the None singleton.

    `credentials_path: str | None`
    :   The type of the None singleton.

    `project_id: str | None`
    :   The type of the None singleton.

    `secret_version: str`
    :   The type of the None singleton.

<a id="SDKConfig"></a>

`SDKConfig(client_id: str, client_secret: str, organization_id: str | None = None, workspace_name: str = 'default')`
:   SDKConfig(client_id: 'str', client_secret: 'str', organization_id: 'str | None' = None, workspace_name: 'str' = 'default')

    ### Instance variables

    `client_id: str`
    :   The type of the None singleton.

    `client_secret: str`
    :   The type of the None singleton.

    `organization_id: str | None`
    :   The type of the None singleton.

    `workspace_name: str`
    :   The type of the None singleton.