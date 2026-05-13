# source-employment-hero: Contributor notes

## Authentication setup

Employment Hero uses bearer token authentication. Code-grant OAuth is not directly supported by the connector.

Create an app in the Employment Hero developer portal to get the OAuth client ID and client secret. The developer portal URL is organization-specific:

```text
https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api
```

## Getting a bearer token with Postman

1. In the Employment Hero developer portal, add an application.
2. Select the scopes needed for testing.
3. Set the redirect URI to `https://oauth.pstmn.io/v1/callback`.
4. Copy the client ID and client secret.
5. In Postman, create a request and open the Authorization tab.
6. Select OAuth 2.0.
7. Set Auth URL to `https://oauth.employmenthero.com/oauth2/authorize`.
8. Set Access Token URL to `https://oauth.employmenthero.com/oauth2/token`.
9. Enter the client ID and client secret.
10. Leave scope and state blank.
11. Click Get New Access Token and approve the authorization in the browser.

Use the returned `access_token` as the connector bearer token.
