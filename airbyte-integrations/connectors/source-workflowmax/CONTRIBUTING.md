# source-workflowmax: Contributor notes

## API documentation

V1 API documentation is available in SwaggerHub:

```text
https://app.swaggerhub.com/apis-docs/WorkflowMax-BlueRock/WorkflowMax-BlueRock-OpenAPI3/0.1#/
```

## Authentication setup

WorkflowMax uses bearer token authentication. Enter the bearer access token in the connector API key field.

## Getting an access token with Postman

1. Open the Authorization tab of an empty HTTP request.
2. Select OAuth 2.0.
3. Set token type to `access token`.
4. Set header prefix to `Bearer`.
5. Set grant type to `Authorization code`.
6. Enable Authorize using browser.
7. Set Auth URL to `https://oauth.workflowmax2.com/oauth/authorize`.
8. Set Access Token URL to `https://oauth.workflowmax2.com/oauth/token`.
9. Set Client ID, Client secret, and Scope from the WorkflowMax application settings. Example scope: `openid profile email workflowmax offline_access`.
10. Set State to any value, such as `1`.
11. Set Client Authentication to Send as Basic Auth Header.
12. Click Get New Access Token.

Use the returned access token as the connector API key.
