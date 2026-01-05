---
sidebar_label: meta
title: airbyte._util.meta
---

Environment meta utils and globals.

This module contains functions for detecting environment and runtime information.

## annotations

## os

## shutil

## sys

## suppress

## lru\_cache

## Path

## python\_implementation

## python\_version

## system

## requests

## get\_version

#### \_MCP\_MODE\_ENABLED

Whether we are running in MCP (Model Context Protocol) mode.

#### COLAB\_SESSION\_URL

URL to get the current Google Colab session information.

#### get\_colab\_release\_version

```python
def get_colab_release_version() -> str | None
```

#### is\_ci

```python
def is_ci() -> bool
```

#### set\_mcp\_mode

```python
def set_mcp_mode() -> None
```

Set flag indicating we are running in MCP (Model Context Protocol) mode.

This should be called early in MCP server initialization to ensure
proper detection and prevent interactive prompts.

#### is\_mcp\_mode

```python
def is_mcp_mode() -> bool
```

Return True if running in MCP (Model Context Protocol) mode.

#### is\_langchain

```python
@lru_cache
def is_langchain() -> bool
```

Return True if running in a Langchain environment.

This checks for the presence of the &#x27;langchain-airbyte&#x27; package.

TODO: A more robust check would inspect the call stack or another flag to see if we are actually
      being invoked via LangChain, vs being installed side-by-side.

This is cached for performance reasons.

#### is\_windows

```python
def is_windows() -> bool
```

#### is\_colab

```python
@lru_cache
def is_colab() -> bool
```

#### is\_interactive

```python
def is_interactive() -> bool
```

Return True if running in an interactive environment where we can prompt users for input.

#### is\_jupyter

```python
@lru_cache
def is_jupyter() -> bool
```

Return True if running in a Jupyter notebook or qtconsole.

Will return False in Colab (use is_colab() instead).

#### get\_notebook\_name

```python
@lru_cache
def get_notebook_name() -> str | None
```

#### get\_vscode\_notebook\_name

```python
@lru_cache
def get_vscode_notebook_name() -> str | None
```

#### is\_vscode\_notebook

```python
def is_vscode_notebook() -> bool
```

#### get\_python\_script\_name

```python
@lru_cache
def get_python_script_name() -> str | None
```

#### get\_application\_name

```python
@lru_cache
def get_application_name() -> str | None
```

#### get\_python\_version

```python
def get_python_version() -> str
```

#### get\_os

```python
def get_os() -> str
```

#### which

```python
@lru_cache
def which(executable_name: str) -> Path | None
```

Return the path to an executable which would be run if the given name were called.

This function is a cross-platform wrapper for the `shutil.which()` function.

#### is\_docker\_installed

```python
def is_docker_installed() -> bool
```

