# source-stripe

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. Events-based incremental sync via StateDelegatingStream with 30-day retention fallback
  2. Silent 403/400/404 error ignoring that can hide missing data
  3. Inaccessible expandable fields in Events API — incremental syncs cannot reconstruct full object state
  4. Populating sandbox data — only add records, do not modify/delete (breaks CATs)
  5. API version-dependent data discrepancies — event payloads reflect the version the object was created with
