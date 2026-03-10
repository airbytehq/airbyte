# source-amazon-seller-partner

## Key Documentation
- See `BEHAVIOR.md` for unique connector behaviors including:
  1. Gzip-compressed report responses in CSV, XML, or JSON formats
  2. Reactive token invalidation on 403 errors via global module reference
  3. Reciprocal Retry-After header interpretation for backoff timing
  4. Regression tests will not run locally — must test via Cloud dev image + progressive rollout
  5. Standard tests fail for vendor forecasting streams (sandbox permission issue since v4.4.7)
  6. Known stream failures in testing — permission errors, timeouts, job failures, invalid input (see tables in BEHAVIOR.md)
