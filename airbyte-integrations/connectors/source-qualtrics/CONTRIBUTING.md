# Contributing to source-qualtrics

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads the Qualtrics API v3.

## Unique behaviors (summary)

1. **Two authentication methods.** A personal API token (`X-API-TOKEN` header) or an OAuth client with the
   Client Credentials grant. For the OAuth path the connector posts to `https://{datacenter}.qualtrics.com/oauth2/token`
   with HTTP Basic client credentials and a form body, keeps the bearer token for 59 minutes (Qualtrics
   issues it for 60) and then requests a new one. Qualtrics grants only the scopes named in the request,
   and rejects the whole request (HTTP 400 `unauthorized_client`) if the client lacks any of them, so the
   default asks for `read:survey_responses` only. That scope was enough for all three endpoints on a live
   account, although Qualtrics' scope table lists `read:surveys` for the survey endpoints.
2. **Use the datacenter shown in Qualtrics IDs.** Qualtrics documents both that API calls are proxied to
   the datacenter where the credentials were created and a `401 DCD_7` error for a mismatched datacenter.
   The connector treats a 401 as a configuration error and points the user at the Datacenter ID setting.
3. **`survey_details` and `survey_response_schemas` read one survey at a time.** Both partition over the
   `surveys` stream and call `GET /surveys/{id}` and `GET /surveys/{id}/response-schema`. The schema
   endpoint allows 60 requests per minute per brand, so the manifest's `api_budget` keeps the connector
   under 55 per minute on that path and `concurrency_level` is 1. A survey that returns 404 (deleted after
   the list was read) is skipped with a log line instead of failing the sync. On 429 the connector waits
   on `Retry-After` if Qualtrics sends it, otherwise backs off exponentially, and gives up after five
   retries.
4. **The response schema record gets a `survey_id`.** The schema document carries the survey id only inside
   its `$id` URL, so the connector adds the parent id as a plain field and primary key.
5. **No survey responses yet.** Qualtrics has no list endpoint for responses. They come from the export
   job flow (`POST /surveys/{id}/export-responses`, poll, download a file), which needs an
   `AsyncRetriever`.
6. **All three streams are full refresh.** `surveys` carries `lastModified`, but the list endpoint has no
   filter on it, and the detail and schema streams have no cursor at all.

## Testing

- Unit tests in `unit_tests/` mock the Qualtrics API with `requests_mock` and run without credentials:

  ```bash
  cd unit_tests && poetry install --no-root && poetry run pytest -q
  ```

- Qualtrics' API reference is public at https://developer-docs.qualtrics.com/docs/public-api/.
