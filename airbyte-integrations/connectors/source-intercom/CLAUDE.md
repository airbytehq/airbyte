# source-intercom

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. Proactive rate limiting that throttles every request based on remaining capacity headers
  2. Companies Scroll API single active scroll constraint (blocks parallel syncs and substreams)
