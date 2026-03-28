# source-sendgrid: Unique Behaviors

## 1. Async Contacts Export with Gzipped CSV Download

The `contacts` stream uses `AsyncRetriever` with a three-phase workflow: POST to `/v3/marketing/contacts/exports` to create an export job, poll the job status until `ready`, then download the result. Unlike all other streams in this connector which use standard synchronous JSON retrieval, the contacts export produces a gzipped CSV file that is decoded via `GzipDecoder` wrapping a `CsvDecoder`.

**Why this matters:** The contacts stream behaves fundamentally differently from every other stream in the connector. It has no pagination, no incremental sync, and returns data in CSV format instead of JSON. Export jobs can take significant time to complete, and if the job fails or times out on SendGrid's side, no partial results are available.
