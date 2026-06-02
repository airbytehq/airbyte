---
id: airbyte_agent_sdk-translation-index
title: airbyte_agent_sdk.translation.index
---

Module airbyte_agent_sdk.translation
====================================
Exception-to-framework-signal translation for tool callables.

Public entry points:

- [`translate_exceptions`](#translate_exceptions) — decorator that wraps a
  sync or async tool callable and converts runtime errors into the active
  framework's retry signal (`ModelRetry` for pydantic-ai,
  `ToolException` for LangChain, return-string for OpenAI Agents,
  `ToolError` for FastMCP).
- `DEFAULT_MAX_OUTPUT_CHARS` — default
  serialized-output size limit (100 KB).

The implementation modules (`_predicates`, `_output`, `_strategies`,
`_decorator`) are private; their underscore prefix marks them as
unsupported. Public consumers should import from `airbyte_agent_sdk` or
this `airbyte_agent_sdk.translation` package only.

Functions
---------

<a id="translate_exceptions"></a>

`translate_exceptions(func: Any = None, *, framework: FrameworkName | None = None, max_output_chars: int | None = 100000, internal_retries: int = 0, should_internal_retry: Callable[[Exception, tuple[Any, ...], dict[str, Any]], bool] | None = None, exhausted_runtime_failure_message: Callable[[Exception, tuple[Any, ...], dict[str, Any]], str | None] | None = None) ‑> Any`
:   Translate tool exceptions into the active framework's retry signal.
    
    Args:
        func: The function to wrap (when used without arguments, e.g.
            `@translate_exceptions`).
        framework: One of `"pydantic_ai" | "langchain" | "openai_agents" |
            "mcp"`. Defaults to None → auto-detect by attempting each
            framework's canonical import in order. Explicit always wins.
        max_output_chars: Maximum serialized output size (`json.dumps`,
            `default=str`). Excess raises the framework's signal asking the
            LLM to narrow the query. Set to `None` or `0` to disable.
        internal_retries: How many transient runtime failures (429/5xx,
            network, timeout) to retry silently before surfacing. Default 0.
        should_internal_retry: Optional predicate `(error, args, kwargs) ->
            bool` further restricting which retryable errors are safe for
            this specific tool.
        exhausted_runtime_failure_message: Optional callback `(error, args,
            kwargs) -> str | None`. Invoked after internal retries are
            exhausted OR were skipped via `should_internal_retry` returning
            False. Return a non-None string to translate the failure
            through the strategy with that custom message; return None to
            translate using the default exception representation.
    
    Returns:
        The wrapped callable. Sync or async is preserved via
        `inspect.iscoroutinefunction`. `functools.wraps` preserves
        `__name__`, `__doc__`, and `__wrapped__`.
    
    Decoration form:
        @translate_exceptions
        def tool(...): ...
    
        @translate_exceptions(framework="pydantic_ai", internal_retries=2)
        async def tool(...): ...