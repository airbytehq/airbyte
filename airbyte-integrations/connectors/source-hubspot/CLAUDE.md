# source-hubspot

## Overview

HubSpot CRM source connector using the declarative (low-code) framework with extensive custom Python
components in `components.py`. The connector syncs data from HubSpot's CRM, marketing, and engagement
APIs.

## Key Files

- `manifest.yaml` -- Declarative stream definitions, authentication, pagination, error handling, and
  schemas (~7600 lines).
- `components.py` -- Custom Python components for behaviors that cannot be expressed in YAML alone.
- `BEHAVIOR.md` -- **Read this first.** Documents all non-obvious connector-specific behaviors
  including hidden API calls during extraction, dual-endpoint selection, pagination workarounds, and
  property chunking. Understanding these behaviors is critical before making changes.

## Important Patterns

- CRM search streams make additional association API calls inside the record extractor. See
  `BEHAVIOR.md` section 1.
- The engagements stream dynamically selects between two different API endpoints. See `BEHAVIOR.md`
  section 2.
- Pagination resets at 10,000 results for search endpoints. See `BEHAVIOR.md` section 3.
- Custom objects use `StateDelegatingStream` with two different sub-stream implementations. See
  `BEHAVIOR.md` section 4.
- Many streams use character-based property chunking (15,000 char limit). See `BEHAVIOR.md` section 5.
- Authentication retries on 401 to handle mid-sync token expiration. See `BEHAVIOR.md` section 8.
