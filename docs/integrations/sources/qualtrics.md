# Qualtrics

The Qualtrics source syncs the surveys of a Qualtrics brand, each survey's full definition and each survey's response schema from the [Qualtrics API v3](https://developer-docs.qualtrics.com/docs/public-api/). It does not sync survey responses yet; see [Limitations](#limitations).

## Prerequisites

- A Qualtrics account with API access. The `surveys` stream returns the surveys the authenticating user owns or that are shared with them or their groups.
- Your **Datacenter ID**, shown under **Account Settings** > **Qualtrics IDs** in the User box (for example `iad1`).
- One of:
  - an OAuth client created in Qualtrics with the **Client Credentials** grant and the `read:survey_responses` scope, or
  - a personal **API token** from **Account Settings** > **Qualtrics IDs**.

## Setup guide

### Set up Qualtrics

Qualtrics supports two ways to authenticate. The OAuth client is the better fit for an integration: its scopes are explicit and its secret can be rotated. It still acts as the user who created it, so that user must be able to see the surveys.

**OAuth client (recommended)**

1. In Qualtrics, open **Account Settings** > **Qualtrics IDs** and note your Datacenter ID.
2. Open the **OAuth Client Manager** and create a client. Choose the **Client Credentials** grant. Qualtrics' [OAuth guide](https://developer-docs.qualtrics.com/docs/public-api/instructions/oauth-authentication-authorization-code/) notes that the grant type selector is only visible to brand administrators and that Client Credentials is the default.
3. Give the client the `read:survey_responses` scope. Qualtrics' scope table lists `read:surveys` for the survey endpoints, but a client with only `read:survey_responses` could read all three streams in testing. Add `read:surveys` to the client and to the **Scopes** setting if your brand enforces it.
4. Copy the client ID and client secret.

Qualtrics grants only the scopes named in each token request, and rejects the request if the client is not authorized for one of them. The connector requests `read:survey_responses` by default; change the **Scopes** setting if your client uses different ones.

**API token**

1. Open **Account Settings** > **Qualtrics IDs**.
2. Under **API**, generate a token and copy it.

See Qualtrics' [OAuth client credentials guide](https://developer-docs.qualtrics.com/docs/public-api/instructions/oauth-authentication/) and [scopes reference](https://developer-docs.qualtrics.com/docs/public-api/instructions/oauthscopes/).

<HideInUI>

### Set up the Qualtrics connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or open your self-managed Airbyte instance.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Qualtrics** from the Source type dropdown.
4. Enter a name for the Qualtrics connector.
5. Enter the **Datacenter ID**.
6. Under **Authentication**, pick **OAuth Client Credentials** and enter the client ID and client secret, or pick **API Token** and enter the token.
7. Click **Set up source**.

</HideInUI>

## Connector settings

| Input | Type | Description | Default |
| --- | --- | --- | --- |
| `datacenter` | `string` | Datacenter that hosts your brand, such as `iad1`, `fra1` or `yul1`, as shown in Qualtrics IDs. | |
| `credentials.auth_type` | `string` | `client_credentials` or `api_token`. | |
| `credentials.client_id` | `string` | OAuth client ID (Client Credentials grant). | |
| `credentials.client_secret` | `string` | OAuth client secret. | |
| `credentials.scope` | `string` | Space-separated scopes to request. The client must be authorized for each one. | `read:survey_responses` |
| `credentials.api_token` | `string` | Personal API token, sent in the `X-API-TOKEN` header. | |

### Connection test

The connection test reads the first page of the `surveys` stream.

## Supported sync modes

The Qualtrics source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

No stream is incremental. The `surveys` list endpoint has no filter on `lastModified`, and the detail and schema endpoints return one document per survey, so every sync re-reads everything.

## Supported streams

| Stream | API endpoint | Primary key | Parent | Records |
| --- | --- | --- | --- | --- |
| `surveys` | `GET /API/v3/surveys` | `id` | | One per survey the credentials can see: id, name, owner, creation and last-modified dates, active flag. |
| `survey_details` | `GET /API/v3/surveys/{id}` | `id` | `surveys` | The full survey definition: questions, blocks, flow, embedded data, export column map, response counts. |
| `survey_response_schemas` | `GET /API/v3/surveys/{id}/response-schema` | `survey_id` | `surveys` | The JSON Schema that describes a response to the survey, with the parent `survey_id` added. |

`survey_details` and `survey_response_schemas` make one request per survey on every sync. A survey that returns `404` because it was deleted after the list was read is skipped with a log line.

### Schemas

`surveys` and the scalar fields of `survey_details` are typed, and the date fields carry the `date-time` format. The nested parts of a survey definition (`questions`, `blocks`, `flow`, `exportColumnMap`, `embeddedData`, `comments`, `loopAndMerge`) are declared as open objects or arrays, because their shape depends on the survey. Destinations store them as JSON or string columns, depending on the destination. The response schema record keeps the JSON Schema document's top-level keys (`$schema`, `$id`, `title`, `description`, `type`, `required`, `properties`). `$schema` and `$id` become column names, and some destinations quote or rename them.

## Performance considerations

Qualtrics' [limits page](https://developer-docs.qualtrics.com/docs/public-api/instructions/limits/) allows 3000 API requests per minute per brand, with lower limits on some endpoints: `GET /surveys/{id}/response-schema` allows 60 per minute. The connector keeps itself under 55 requests per minute on that endpoint and reads one stream at a time, so a brand with more than 55 surveys spends at least one minute per 55 surveys on `survey_response_schemas`. On `429`, it waits on the `Retry-After` header if Qualtrics sends one, otherwise backs off exponentially, and gives up after five retries.

OAuth access tokens last one hour. The connector requests a new one after 59 minutes.

## Limitations & Troubleshooting

### Limitations

- **No survey responses.** Qualtrics does not offer a list endpoint for responses. They are retrieved with an export job (`POST /surveys/{id}/export-responses`, then polling and a file download), which this version does not implement.
- **Three streams.** Users, groups, distributions, directories and contacts are not included yet.
- **One brand per source.** Credentials belong to one brand on one datacenter. Create one source per brand.

### Errors

| Error | Cause | Fix |
| --- | --- | --- |
| `Qualtrics rejected the client ID or client secret` | The token request returned `400` or `401`. A `400` with `unauthorized_client` means the client is not authorized for one of the requested scopes. | Check the client ID and secret, that the client uses the Client Credentials grant, that **Scopes** names only scopes the client has, and that **Datacenter ID** is the datacenter the client was created in. |
| `Qualtrics rejected the credentials for this request` | A data request returned `401` or `403`. | For an API token, generate a new one. For OAuth, check the scope and that **Datacenter ID** is the one shown in Qualtrics IDs. |
| `Survey not found` in the logs | `GET /surveys/{id}` or the response schema returned `404`, usually because the survey was deleted after the list was read. | Nothing. The survey is skipped and the sync continues. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                       |
| ------- | ---------- | --------------------------------------------------------- | --------------------------------------------- |
| 0.0.1   | 2026-11-25 | [XXXXX](https://github.com/airbytehq/airbyte/pull/XXXXX)  | Initial release by [@MercureTony](https://github.com/MercureTony) |

</details>
