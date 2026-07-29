# CDK Investigation Map

The canonical map the **Grounding CDK deep-dive** follows. API sources are thin
declarative/Python layers over `airbyte-python-cdk`, so a finding about a paginator,
cursor, or extractor is only trustworthy when checked against how the CDK *actually*
behaves — at the version the connector **runs on**.

**Read the connector's PINNED CDK worktree. `origin/main` is a secondary, upgrade-only
reference.** Never from memory, never from a stale checkout. The deep-dive emits an
evidence brief injected into every reviewer, with each claim labelled `PINNED` or `MAIN`.

All paths are under `airbyte_cdk/sources/declarative/` unless noted. **Paths drift between
CDK versions** — several entries below were wrong at one point because a module was renamed.
If a path does not exist in the worktree you are reading, `Glob` for the component name
rather than concluding the component is absent.

## Always read first (the manifest contract + runtime behavior)

| File | Why |
|------|-----|
| `declarative_component_schema.yaml` | The authoritative manifest contract — which components and fields legally exist at this CDK version. A manifest field absent from the **pinned** schema is a hard error in the PR, not a style note. A field present on main but absent from the pinned schema is *not available to this connector*. |
| `parsers/model_to_component_factory.py` | Maps manifest YAML → Python classes. What a component **actually does** at runtime (defaults, wiring, side effects). |

## Component-family targets (read the ones the diff touches)

| If the PR touches… | Read these CDK sources | Establish |
|--------------------|------------------------|-----------|
| **Pagination** | `requesters/paginators/default_paginator.py`, `requesters/paginators/no_pagination.py`, `requesters/paginators/strategies/{cursor_pagination_strategy,offset_increment,page_increment,stop_condition}.py` | Stop-condition & record-filter interaction, page-size limits, cursor/next-token extraction, end-of-pages detection |
| **Incremental / cursor** | `incremental/` (incl. `concurrent_partition_cursor.py`), `datetime/`, `../connector_state_manager.py` | Checkpointing, slice/date-window boundaries, state format, concurrent-cursor semantics |
| **Extraction / records** | `extractors/{dpath_extractor,record_selector,record_filter,response_to_file_extractor}.py` | `field_path` semantics, filter-before/after-pagination, empty-page handling |
| **Auth** | `auth/{oauth,jwt,token,token_provider,selective_authenticator,declarative_authenticator}.py` | Token refresh flow, header/param placement, scope correctness, selective auth |
| **Error / retry** | `requesters/error_handlers/{default_error_handler,composite_error_handler,http_response_filter,default_http_response_filter}.py`, `error_handlers/backoff_strategies/` | 429/5xx handling, `Retry-After`, backoff, retryable-vs-fatal classification |
| **Requester / request options** | `requesters/http_requester.py`, `requesters/request_options/`, `requesters/query_properties/`, `requesters/request_option.py` | Request shape, param/body/header injection, query-property batching |
| **Partitioning / substreams** | `partition_routers/{substream_partition_router,list_partition_router,cartesian_product_stream_slicer,grouping_partition_router}.py` | Parent-stream slicing, parent-key mapping, request-option injection per slice — and whether the **partition-key shape** changed, which invalidates per-partition incremental state (breaking without a state migration) |
| **Transformations** | `transformations/{add_fields,remove_fields,flatten_fields,dpath_flatten_fields}.py`, `transformations/{keys_to_snake_transformation,keys_to_lower_transformation,keys_replace_transformation}.py`, `transformations/config_transformations/` | Whether the transform belongs at extractor vs transformer layer, field-level effects — and critically, whether it changes the **value** of an existing primary-key or cursor field (a breaking re-key) |
| **Schema** | `schema/{default_schema_loader,inline_schema_loader,json_file_schema_loader,dynamic_schema_loader,composite_schema_loader}.py` | Inline vs file vs dynamic schema loading; whether dynamic schema is warranted |
| **Async jobs / bulk** | `async_job/`, `retrievers/async_retriever.py`, `requesters/http_job_repository.py` | Async job lifecycle, polling, download; correct for this API's bulk/export model |
| **Retrieval** | `retrievers/{simple_retriever,async_retriever}.py`, `retrievers/pagination_tracker.py` | Retriever wiring of requester + paginator + extractor + slicer |

## Type-specific extras

| Connector type | Extra targets |
|----------------|---------------|
| **low-code-components** / **custom-python** | The base class each `components.py` custom component subclasses + `parsers/custom_code_compiler.py`. Ask: is the custom component necessary, or does a declarative component already cover it? |
| **custom-python** | `airbyte_cdk/sources/streams/` (`HttpStream`/`Stream`), `airbyte_cdk/sources/streams/http/` — subclassing, method overrides, retry/backoff hooks |
| **file-based-api** | `airbyte_cdk/sources/file_based/` — stream config, parsers, the API-auth path |
| **concurrent** | `concurrent_declarative_source.py`, `airbyte_cdk/sources/concurrent_source/` — concurrency level, thread-pool semantics |

## Version awareness — which CDK is authoritative

**The connector's PINNED CDK is the authoritative behaviour reference. `origin/main` is a
secondary, upgrade-only reference.** The pinned version is what executes in production, so
it is what the PR must be correct against.

Resolve the pinned version **from the PR head**, not the working tree:

| Connector type | Where the pin lives |
|---|---|
| manifest-only, low-code-components, hybrid on an SDM base | `metadata.yaml` → `connectorBuildOptions.baseImage`. A `source-declarative-manifest:<tag>` tag **is** the CDK version. |
| custom-python, or any connector on `python-connector-base` | the `airbyte-cdk` pin in `pyproject.toml` (record the *resolved* version if the pin is a range) |

Normalise a dev tag (`7.16.0.post1.dev23950401533` → base `7.16.0`) and note that the pinned
worktree is then approximate.

### Why the direction matters

Reviewing against main instead of the pinned version produces two specific, recurring errors:

1. **False positive** — flagging a correct hand-rolled implementation as "reinventing what
   the CDK provides", when the component that would replace it landed *after* the connector's
   pin and is therefore unavailable.
2. **False negative** — missing that the manifest uses a component or field main has but the
   pinned schema does not. That is a hard runtime error, and a main-based read sees nothing
   wrong with it.

So: anything you find only on main goes in `only_on_main` and is reported as an **upgrade
opportunity**, never as an available fix.

### `cdk_version_mismatch`

Flag it when the PR:

- uses a manifest component/field **absent from the pinned schema** (hard error), or
- re-implements behaviour the **pinned** CDK already provides, or
- depends on behaviour that differs between the pinned version and main (say which way).

### The worked example

CDK `v7.21.0` carries `fix #1073 — prevent record filters from prematurely stopping
PageIncrement pagination`. A connector pinned **below** that fix genuinely exhibits the bug,
so a PR working around it is *correct for its version* — and telling the author to delete the
workaround because "main handles this" would break the connector. A connector pinned **at or
above** it should not carry the workaround. Only a pinned-version read tells those two cases
apart. This is the class of error the deep-dive exists to catch, and getting the authority
direction backwards is how the deep-dive causes it instead.
