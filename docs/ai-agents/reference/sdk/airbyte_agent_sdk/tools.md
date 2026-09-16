---
id: airbyte_agent_sdk-tools
title: airbyte_agent_sdk.tools
---

Module airbyte_agent_sdk.tools
==============================
Framework-ready connector tools.

Functions
---------

<a id="build_agent_tool_decorator"></a>

`build_agent_tool_decorator(model: Any, *, role: AgentToolRole | None = None, inspect_tool: str | None = None, docs_tool: str | None = None, max_output_chars: int | None | Unset = UNSET, framework: FrameworkName = 'none', internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Callable[[Callable[..., typing.Any]], Callable[..., typing.Any]]`
:   Build the `agent_tool` decorator bound to one connector model.
    
    Backs the generated ``@<Connector>.agent_tool(...)`` classmethod, which
    documents the user-facing contract. Always uses progressive skill docs:
    the execute docstring points the agent at the connector's inspect and
    docs tools instead of embedding the full entity/action reference.

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

<a id="SkillDocsAccessor"></a>

`SkillDocsAccessor(connector: Any, *, docs_provider: ConnectorDocsProvider | None = None)`
:   Stateful access to one connector's skill docs.
    
    Owns the ``docs_skill_id`` cache: populated after the first successful
    :meth:`inspect`, re-inspected only when missing, never populated on
    failure. Cache lifetime is the accessor instance — `build_connector_tools`
    shares one across its tool closures; generated typed connectors hold one
    per connector instance.

    ### Instance variables

    `provider: ConnectorDocsProvider | None`
    :

    ### Methods

    `inspect(self) ‑> dict[str, typing.Any]`
    :   Inspect the connector's hosted metadata and resolve its docs skill id.
        
        Local/offline connectors (no docs provider) get a local-mode payload
        with a warning instead of a hosted inspection.

    `read(self, section: str | None = None) ‑> str`
    :   Read the connector's usage docs, rendered to text.
        
        Omit ``section`` for the outline and general guidance; pass an exact
        section id for full details. Local/offline connectors return the full
        generated docs and ignore ``section``.

<a id="Unset"></a>

`Unset()`
:   Sentinel type marking 'argument not provided' (distinct from None).