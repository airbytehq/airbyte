---
id: airbyte_agent_sdk-deprecated_action_aliases
title: airbyte_agent_sdk.deprecated_action_aliases
---

Module airbyte_agent_sdk.deprecated_action_aliases
==================================================
Deprecated action-name aliases kept for a migration window.

Scrub plan (target: after 2026-10-01): delete this module, remove its call sites
(grep `deprecated_action_aliases`), and delete `tests/test_deprecated_action_aliases.py`.
Orb metering intentionally keeps reporting `api_search` (see `_ORB_TOOL_CALLS_ACTION_ALIASES`
in `backend/app/core/orb_outbox.py`); leave that mapping in place unless billing agrees to rename.

Functions
---------

<a id="resolve_action_alias"></a>

`resolve_action_alias(action: str) ‑> str`
: