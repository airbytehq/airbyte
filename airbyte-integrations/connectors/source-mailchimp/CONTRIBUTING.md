# source-mailchimp: Unique Behaviors

## 1. Dynamic API Base URL Determined by Data Center Extraction

Mailchimp's API requires all requests to be sent to a data-center-specific subdomain (e.g., `us20.api.mailchimp.com`). The connector determines the correct data center at config time through one of two methods depending on the auth type:

- **API key auth:** The data center is extracted from the API key suffix (e.g., `abc123-us20` yields `us20`).
- **OAuth:** The connector makes an HTTP request to `https://login.mailchimp.com/oauth2/metadata` using the access token, and extracts the `dc` field from the response.

This happens in `ExtractAndSetDataCenterConfigValue`, a config transformation that runs before any data syncing begins. If the metadata endpoint returns a 200 with `"error": "invalid_token"`, it raises a config error rather than proceeding with an invalid token.

**Why this matters:** The API base URL is not static and cannot be hardcoded. If the data center extraction fails or returns an incorrect value, all subsequent API calls will go to the wrong host and fail silently or with confusing errors. The OAuth path also means a network call happens during config validation, before any sync starts.
