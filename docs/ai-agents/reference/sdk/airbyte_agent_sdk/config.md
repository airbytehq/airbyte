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
    consulted when ``SECRETS_CONFIGURED_FROM_ENVIRONMENT=true``.

<a id="resolve_credentials"></a>

`resolve_credentials(*, client_id: str | None = None, client_secret: str | None = None, organization_id: str | None = None, workspace_name: str | None = None) ‑> tuple[str, str, str | None, str]`
:   Resolve credentials: explicit arg -> global config -> env var.
    
    Returns (client_id, client_secret, organization_id, workspace_name).
    Raises ValueError if client_id or client_secret cannot be resolved.

Classes
-------

<a id="AWSDataPlaneCredentials"></a>

`AWSDataPlaneCredentials(access_key_id: str | None = None, secret_access_key: str | None = None, session_token: str | None = None, region_name: str | None = None)`
:   AWS credentials for the customer's data plane.
    
    Consulted only on the local hydration path, which is enabled by
    ``SECRETS_CONFIGURED_FROM_ENVIRONMENT=true``. Any field may be ``None``:
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