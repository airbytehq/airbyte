---
sidebar_label: _tool_utils
title: airbyte.mcp._tool_utils
---

MCP tool utility functions.

This module provides a decorator to tag tool functions with MCP annotations
for deferred registration with safe mode filtering.

## annotations

## inspect

## os

## warnings

## Callable

## lru\_cache

## Any

## Literal

## TypeVar

## AIRBYTE\_MCP\_DOMAINS

## AIRBYTE\_MCP\_DOMAINS\_DISABLED

## MCP\_TOOL\_DOMAINS

## DESTRUCTIVE\_HINT

## IDEMPOTENT\_HINT

## OPEN\_WORLD\_HINT

## READ\_ONLY\_HINT

#### F

#### AIRBYTE\_CLOUD\_MCP\_READONLY\_MODE

#### AIRBYTE\_CLOUD\_MCP\_SAFE\_MODE

#### AIRBYTE\_CLOUD\_WORKSPACE\_ID\_IS\_SET

#### \_REGISTERED\_TOOLS

#### \_GUIDS\_CREATED\_IN\_SESSION

## SafeModeError Objects

```python
class SafeModeError(Exception)
```

Raised when a tool is blocked by safe mode restrictions.

#### register\_guid\_created\_in\_session

```python
def register_guid_created_in_session(guid: str) -> None
```

Register a GUID as created in this session.

**Arguments**:

- `guid` - The GUID to register

#### check\_guid\_created\_in\_session

```python
def check_guid_created_in_session(guid: str) -> None
```

Check if a GUID was created in this session.

This is a no-op if AIRBYTE_CLOUD_MCP_SAFE_MODE is set to &quot;0&quot;.

Raises SafeModeError if the GUID was not created in this session and
AIRBYTE_CLOUD_MCP_SAFE_MODE is set to 1.

**Arguments**:

- `guid` - The GUID to check

#### \_resolve\_mcp\_domain\_filters

```python
@lru_cache(maxsize=1)
def _resolve_mcp_domain_filters() -> tuple[set[str], set[str]]
```

Resolve MCP domain filters from environment variables.

This function is cached to ensure warnings are only emitted once per process.

**Returns**:

  Tuple of (enabled_domains, disabled_domains) as sets.
  If an env var is not set, the corresponding set will be empty.

#### is\_domain\_enabled

```python
def is_domain_enabled(domain: str) -> bool
```

Check if a domain is enabled based on AIRBYTE_MCP_DOMAINS and AIRBYTE_MCP_DOMAINS_DISABLED.

The logic is:
- If neither env var is set: all domains are enabled
- If only AIRBYTE_MCP_DOMAINS is set: only those domains are enabled
- If only AIRBYTE_MCP_DOMAINS_DISABLED is set: all domains except those are enabled
- If both are set: disabled domains subtract from enabled domains

**Arguments**:

- `domain` - The domain to check (e.g., &quot;cloud&quot;, &quot;local&quot;, &quot;registry&quot;)
  

**Returns**:

  True if the domain is enabled, False otherwise

#### should\_register\_tool

```python
def should_register_tool(annotations: dict[str, Any]) -> bool
```

Check if a tool should be registered based on mode settings.

**Arguments**:

- `annotations` - Tool annotations dict containing domain, readOnlyHint, and destructiveHint
  

**Returns**:

  True if the tool should be registered, False if it should be filtered out

#### get\_registered\_tools

```python
def get_registered_tools(
    domain: Literal["cloud", "local", "registry"] | None = None
) -> list[tuple[Callable[..., Any], dict[str, Any]]]
```

Get all registered tools, optionally filtered by domain.

**Arguments**:

- `domain` - The domain to filter by (e.g., &quot;cloud&quot;, &quot;local&quot;, &quot;registry&quot;).
  If None, returns all tools.
  

**Returns**:

  List of tuples containing (function, annotations) for each registered tool

#### mcp\_tool

```python
def mcp_tool(domain: Literal["cloud", "local", "registry"],
             *,
             read_only: bool = False,
             destructive: bool = False,
             idempotent: bool = False,
             open_world: bool = False,
             extra_help_text: str | None = None) -> Callable[[F], F]
```

Decorator to tag an MCP tool function with annotations for deferred registration.

This decorator stores the annotations on the function for later use during
deferred registration. It does not register the tool immediately.

**Arguments**:

- `domain` - The domain this tool belongs to (e.g., &quot;cloud&quot;, &quot;local&quot;, &quot;registry&quot;)
- `read_only` - If True, tool only reads without making changes (default: False)
- `destructive` - If True, tool modifies/deletes existing data (default: False)
- `idempotent` - If True, repeated calls have same effect (default: False)
- `open_world` - If True, tool interacts with external systems (default: False)
- `extra_help_text` - Optional text to append to the function&#x27;s docstring
  with a newline delimiter
  

**Returns**:

  Decorator function that tags the tool with annotations
  

**Example**:

  @mcp_tool(&quot;cloud&quot;, read_only=True, idempotent=True)
  def list_sources():
  ...

#### register\_tools

```python
def register_tools(app: Any, domain: Literal["cloud", "local",
                                             "registry"]) -> None
```

Register tools with the FastMCP app, filtered by domain and safe mode settings.

**Arguments**:

- `app` - The FastMCP app instance
- `domain` - The domain to register tools for (e.g., &quot;cloud&quot;, &quot;local&quot;, &quot;registry&quot;)

