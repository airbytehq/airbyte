# source-monday

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. GraphQL API with schema-driven query building and stream-specific query patterns
  2. Two-level nested pagination for items (boards outer, items inner)
  3. Cursor expiration after 60 minutes triggers RESET_PAGINATION (full re-read)
