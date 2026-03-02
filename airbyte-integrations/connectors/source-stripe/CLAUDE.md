# source-stripe

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. Events-based incremental sync via StateDelegatingStream with 30-day retention fallback
  2. Silent 403/400/404 error ignoring that can hide missing data
