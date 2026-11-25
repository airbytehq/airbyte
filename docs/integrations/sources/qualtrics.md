# Qualtrics

The Qualtrics source syncs the surveys of a Qualtrics brand, each survey's full definition and each survey's response schema from the [Qualtrics API v3](https://developer-docs.qualtrics.com/docs/public-api/). It does not sync survey responses yet; see [Limitations](#limitations).

## Prerequisites

- A Qualtrics account with API access. Listing surveys requires a user who can see them, typically a brand administrator or the survey owner.
- Your **Datacenter ID**, the first part of your Qualtrics URL (for example `iad1` in `https://iad1.qualtrics.com`). It is also shown under **Account Settings** > **Qualtrics IDs**.
- One of:
  - an OAuth client created in Qualtrics with the **Client Credentials** grant and the `read:surveys` and `read:survey_responses` scopes, or
  - a personal **API token** from **Account Settings** > **Qualtrics IDs**.

## Setup guide

### Set up Qualtrics

Qualtrics supports two ways to authenticate. The OAuth client is the better fit for an integration, because it is not tied to one person's login.

**OAuth client (recommended)**

1. In Qualtrics, open **Account Settings** > **Qualtrics IDs** and note your Datacenter ID.
2. Open the **OAuth Client Manager** and create a client. Choose the **Client Credentials** grant. The grant type selector is only visible to brand administrators, and Client Credentials is the default.
3. Give the client the `read:surveys` and `read:survey_responses` scopes.
4. Copy the client ID and client secret.

Qualtrics grants only the scopes named in each token request, never the client's full set. The connector requests `read:surveys read:survey_responses` by default; change the **Scopes** setting if your client uses different ones.

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
| `datacenter` | `string` | Datacenter that hosts your brand, such as `iad1`, `fra1` or `yul1`. Tokens and API calls must go to the same datacenter. | |
| `credentials.auth_type` | `string` | `client_credentials` or `api_token`. | |
| `credentials.client_id` | `string` | OAuth client ID (Client Credentials grant). | |
| `credentials.client_secret` | `string` | OAuth client secret. | |
| `credentials.scope` | `string` | Space-separated scopes to request. | `read:surveys read:survey_responses` |
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

`survey_details` and `survey_response_schemas` make one request per survey on every sync.

### Schemas

`surveys` and the scalar fields of `survey_details` are typed, and the date fields carry the `date-time` format. The nested parts of a survey definition (`questions`, `blocks`, `flow`, `exportColumnMap`, `embeddedData`, `comments`, `loopAndMerge`) are declared as open objects or arrays, because their shape depends on the survey. Typed destinations store them as JSON. The response schema record keeps the JSON Schema document's top-level keys (`$schema`, `$id`, `title`, `description`, `type`, `required`, `properties`).

## Performance considerations

Qualtrics allows 3000 API requests per minute per brand, with lower limits on some endpoints: `GET /surveys/{id}/response-schema` allows 60 per minute. A brand with many surveys therefore spends most of a sync of `survey_response_schemas` waiting. The connector honors the `Retry-After` header on `429` responses, falls back to exponential backoff, and retries up to five times. See Qualtrics' [limits page](https://developer-docs.qualtrics.com/docs/public-api/instructions/limits/).

OAuth access tokens last one hour. The connector requests a new one after 59 minutes.

## Limitations & Troubleshooting

### Limitations

- **No survey responses.** Qualtrics does not offer a list endpoint for responses. They are retrieved with an export job (`POST /surveys/{id}/export-responses`, then polling and a file download), which this version does not implement.
- **Three streams.** Users, groups, distributions, directories and contacts are not included yet.
- **One brand per source.** Credentials belong to one brand on one datacenter. Create one source per brand.

### Errors

| Error | Cause | Fix |
| --- | --- | --- |
| `Qualtrics rejected the client ID or client secret` | The token request returned `400` or `401`. | Check the client ID and secret, that the client uses the Client Credentials grant and has the requested scopes, and that **Datacenter ID** is the datacenter the client was created in. |
| `Qualtrics rejected the credentials for this request` | A data request returned `401` or `403`. | For an API token, generate a new one. For OAuth, check the scopes and the datacenter. Tokens from one datacenter are rejected by another. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                       |
| ------- | ---------- | --------------------------------------------------------- | --------------------------------------------- |
| 0.0.1   | 2026-11-25 | [XXXXX](https://github.com/airbytehq/airbyte/pull/XXXXX)  | Initial release by [@MercureTony](https://github.com/MercureTony) |

</details>
