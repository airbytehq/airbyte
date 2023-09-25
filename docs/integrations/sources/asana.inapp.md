## Prerequisites

* OAuth access or a Personal Access Token

## Setup guide
1. Enter a name for your source
2. Authenticate using OAuth (recommended) or enter your `personal_access_token`. Please follow these [steps](https://developers.asana.com/docs/personal-access-token) to obtain a Personal Access Token for your account.
3. Click **Set up source**

### Syncing Multiple Projects
If you have access to multiple projects, Airbyte will sync data related to all projects you have access to. The ability to filter to specific projects is not available at this time.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Asana](https://docs.airbyte.com/integrations/sources/asana).