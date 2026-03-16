# source-slack

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. Auto-joining channels during sync via POST side-effect calls
  2. Dynamic rate limit policy that switches from unlimited to 1 req/min on first 429
