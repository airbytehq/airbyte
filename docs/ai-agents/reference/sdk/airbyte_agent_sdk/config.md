---
id: airbyte_agent_sdk-config
title: airbyte_agent_sdk.config
---

Module airbyte_agent_sdk.config
===============================
Global SDK configuration for Airbyte credentials.

Functions
---------

`configure(*, client_id: str, client_secret: str, organization_id: str | None = None, workspace_name: str = 'default') ‑> None`
:   Set global SDK credentials. These are used as defaults by connect(), Workspace, and ask().
    
    Calling configure() again overwrites the previous configuration.
    Explicit kwargs passed to connect()/Workspace()/ask() always take priority.

`get_config() ‑> airbyte_agent_sdk.config.SDKConfig | None`
:   

`resolve_credentials(*, client_id: str | None = None, client_secret: str | None = None, organization_id: str | None = None, workspace_name: str | None = None) ‑> tuple[str, str, str | None, str]`
:   Resolve credentials: explicit arg -> global config -> env var.
    
    Returns (client_id, client_secret, organization_id, workspace_name).
    Raises ValueError if client_id or client_secret cannot be resolved.

Classes
-------

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