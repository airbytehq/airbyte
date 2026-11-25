# Contributing to source-qualtrics

For general guidance on contributing to Airbyte connectors, see the
[Connector Development documentation](https://docs.airbyte.com/connector-development/).

This is a manifest-only connector: all behavior lives in `manifest.yaml`. It reads the Qualtrics API v3.

## Unique behaviors (summary)

1. **Two authentication methods.** A personal API token (`X-API-TOKEN` header) or an OAuth client with the
   Client Credentials grant. For the OAuth path the connector posts to `https://{datacenter}.qualtrics.com/oauth2/token`
   with HTTP Basic client credentials and a form body, keeps the bearer token for 59 minutes (Qualtrics
   issues it for 60) and then requests a new one. Qualtrics grants only the scopes named in the request,
   never the client's whole set, so the `scope` setting matters.
2. **Tokens are tied to a datacenter.** A token requested from one datacenter is rejected by another, so a
   wrong `datacenter` fails as a configuration error on the first request.
3. **`survey_details` and `survey_response_schemas` read one survey at a time.** Both partition over the
   `surveys` stream and call `GET /surveys/{id}` and `GET /surveys/{id}/response-schema`. The schema
   endpoint allows 60 requests per minute per brand, so a brand with many surveys spends most of its sync
   time waiting on `Retry-After`.
4. **The response schema record gets a `survey_id`.** Qualtrics' schema document does not name its survey, so
   the connector adds the parent id as the primary key.
5. **No survey responses yet.** Qualtrics has no list endpoint for responses. They come from the export
   job flow (`POST /surveys/{id}/export-responses`, poll, download a file), which needs an
   `AsyncRetriever`. A community draft once pointed an incremental stream at `GET /surveys/{id}/responses`,
   an endpoint that does not exist.
6. **All three streams are full refresh.** `surveys` carries `lastModified`, but the list endpoint has no
   filter on it, and the detail and schema streams have no cursor at all.

## Testing

- Unit tests in `unit_tests/` mock the Qualtrics API with `requests_mock` and run without credentials:

  ```bash
  cd unit_tests && poetry install --no-root && poetry run pytest -q
  ```

- Qualtrics' API reference is public at https://developer-docs.qualtrics.com/docs/public-api/.
