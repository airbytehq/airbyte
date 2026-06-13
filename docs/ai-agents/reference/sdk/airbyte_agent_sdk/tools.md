---
id: airbyte_agent_sdk-tools
title: airbyte_agent_sdk.tools
---

Module airbyte_agent_sdk.tools
==============================
Framework-ready connector tools.

Functions
---------

<a id="build_connector_tools"></a>

`build_connector_tools(connector: Any, *, framework: FrameworkName | None = None, docs_provider: ConnectorDocsProvider | None = None, use_progressive_docs: bool = True, max_output_chars: int | None = 100000, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> airbyte_agent_sdk.tools.ConnectorTools`
:   Build inspect/docs/execute tools bound to a single connector.
    
    Hosted connectors use the live inspect and skill-docs endpoints. Local
    connectors keep the generated YAML-derived rich docs as their fallback.

Classes
-------

<a id="ConnectorDocsProvider"></a>

`ConnectorDocsProvider(*args, **kwargs)`
:   Provider of connector inspection and skill-doc endpoints.

    ### Ancestors (in MRO)

    * typing.Protocol
    * typing.Generic

    ### Methods

    `inspect_connector(self) ‑> dict[str, typing.Any]`
    :

    `read_skill_docs(self, id: str, section: str | None = None) ‑> dict[str, typing.Any]`
    :

<a id="ConnectorTools"></a>

`ConnectorTools(inspect_connector: ToolCallable, read_skill_docs: ToolCallable, execute: ToolCallable, use_progressive_docs: bool = True)`
:   Connector tool callables for agent frameworks.

    ### Instance variables

    `execute: Callable[..., typing.Awaitable[typing.Any]]`
    :   The type of the None singleton.

    `inspect_connector: Callable[..., typing.Awaitable[typing.Any]]`
    :   The type of the None singleton.

    `read_skill_docs: Callable[..., typing.Awaitable[typing.Any]]`
    :   The type of the None singleton.

    `use_progressive_docs: bool`
    :   The type of the None singleton.

    ### Methods

    `as_list(self) ‑> list[Callable[..., typing.Awaitable[typing.Any]]]`
    :