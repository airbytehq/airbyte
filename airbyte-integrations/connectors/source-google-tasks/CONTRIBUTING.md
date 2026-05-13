# source-google-tasks: Contributor notes

## Getting a bearer token with Postman

Code-grant OAuth 2.0 is not directly supported by the connector. Use Postman to get a bearer token, then use the token as the connector `api_key`.

1. In Google Cloud, enable the Tasks API:

   ```text
   https://console.cloud.google.com/apis/api/tasks.googleapis.com/metrics
   ```

2. Open the OAuth consent screen and add your email for testing access:

   ```text
   https://console.cloud.google.com/apis/credentials/consent
   ```

3. Open Credentials and create OAuth 2.0 credentials:

   ```text
   https://console.cloud.google.com/apis/credentials
   ```

4. Copy the client ID and client secret.
5. Add `https://oauth.pstmn.io/v1/callback` as the callback URL.
6. In Postman, open a new request and set Authorization to OAuth 2.0.
7. Set scope to `https://www.googleapis.com/auth/tasks https://www.googleapis.com/auth/tasks.readonly`.
8. Set Access Token URL to `https://accounts.google.com/o/oauth2/token`.
9. Set Auth URL to `https://accounts.google.com/o/oauth2/v2/auth`.
10. Click Get New Access Token and authorize with your Google account.
11. Copy the bearer token and use it as the connector credential.
