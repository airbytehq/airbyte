# source-azure-blob-storage: Contributor notes

## Generating an OAuth token

The tenant ID must come from the user who owns the Azure tenant.

1. Open the authorization URL:

   ```text
   https://login.microsoftonline.com/<tenant_id>/oauth2/v2.0/authorize
     ?response_type=code
     &client_id=<client_id>
     &scope=offline_access https://storage.azure.com/.default
     &redirect_uri=http://localhost:8000/auth_flow
     &response_mode=query
     &state=1234
   ```

2. Exchange the returned code for a token:

   ```text
   POST https://login.microsoftonline.com/<tenant_id>/oauth2/v2.0/token
   client_id: <client_id>
   code: <code from the authorization response>
   redirect_uri: http://localhost:8000/auth_flow
   grant_type: authorization_code
   client_secret: <client_secret>
   ```
