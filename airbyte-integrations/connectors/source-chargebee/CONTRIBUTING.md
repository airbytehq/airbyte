# source-chargebee: Unique Behaviors

## 1. Product Catalog Version-Gated Streams

Chargebee has two incompatible Product Catalog versions (1.0 and 2.0), and many streams only work with one version. When a stream is requested against the wrong Product Catalog version, the API returns a response with `api_error_code: configuration_incompatible`. The connector silently ignores these responses via a predicate-based error filter rather than failing the sync.

**Why this matters:** A Chargebee account on Product Catalog 2.0 will silently produce zero records for streams that only exist in Product Catalog 1.0 (like `addon`), and vice versa. There is no upfront validation of which catalog version the account uses, so streams quietly return empty rather than raising an error explaining the incompatibility.
