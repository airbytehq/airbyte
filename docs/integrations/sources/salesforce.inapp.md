## Prerequisites

- [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
- (Optional, Recommended) Dedicated Salesforce [user](https://help.salesforce.com/s/articleView?id=adding_new_users.htm&type=5&language=en_US)
<!-- env:oss -->
- (For Airbyte Open Source) Salesforce [OAuth](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_tokens_scopes.htm&type=5) credentials
<!-- /env:oss -->

## Setup guide

### Step 1: (Optional, Recommended) Create a read-only Salesforce user

While you can set up the Salesforce connector using any Salesforce user with read permission, we recommend creating a dedicated read-only user for Airbyte. This allows you to granularly control the data Airbyte can read.

To create a dedicated read only Salesforce user:

1. [Log in to Salesforce](https://login.salesforce.com/) with an admin account.
2. On the top right of the screen, click the gear icon and then click **Setup**.
3. In the left navigation bar, under Administration, click **Users** > **Profiles**. The Profiles page is displayed. Click **New profile**.
4. For Existing Profile, select **Read only**. For Profile Name, enter **Airbyte Read Only User**.
5. Click **Save**. The Profiles page is displayed. Click **Edit**.
6. Scroll down to the **Standard Object Permissions** and **Custom Object Permissions** and enable the **Read** checkbox for objects that you want to replicate via Airbyte.
7. Scroll to the top and click **Save**.
8. On the left side, under Administration, click **Users** > **Users**. The All Users page is displayed. Click **New User**.
9. Fill out the required fields:
   1. For License, select **Salesforce**.
   2. For Profile, select **Airbyte Read Only User**.
   3. For Email, make sure to use an email address that you can access.
10. Click **Save**.
11. Copy the Username and keep it accessible.
12. Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

<!-- env:oss -->

### For Airbyte Open Source only: Obtain Salesforce OAuth credentials

If you are using Airbyte Open Source, you will need to obtain the following OAuth credentials to authenticate:

- Client ID
- Client Secret
- Refresh Token

To obtain these credentials, follow [this walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) with the following modifications:

   1. If your Salesforce URL is not in the `X.salesforce.com` format, use your Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`.
   2. When running a curl command, run it with the `-L` option to follow any redirects.
   3. If you [created a read-only user](https://docs.google.com/document/d/1wZR8pz4MRdc2zUculc9IqoF8JxN87U40IqVnTtcqdrI/edit#heading=h.w5v6h7b2a9y4), use the user credentials when logging in to generate OAuth tokens.

<!-- /env:oss -->

### Step 2: Set up the Salesforce connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Salesforce** from the list of available sources.
4. Enter a **Source name** of your choosing to help you identify this source.
5. To authenticate:
<!-- env:cloud -->
**For Airbyte Cloud**: Click **Authenticate your account** to authorize your Salesforce account. Airbyte will authenticate the Salesforce account you are already logged in to. Please make sure you are logged into the right account.
<!-- /env:cloud -->
<!-- env:oss -->
**For Airbyte Open Source**: Enter your Client ID, Client Secret, and Refresh Token.
<!-- /env:oss -->
6. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
7. (Optional) For **Start Date**, use the provided datepicker or enter the date programmatically in either `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` format. The data added on and after this date will be replicated. If this field is left blank, Airbyte will replicate the data for the last two years by default. Please note that timestamps are in [UTC](https://www.utctime.net/).
8. (Optional) In the **Filter Salesforce Object** section, you may choose to target specific data for replication. To do so, click **Add**, then select the relevant criteria from the **Search criteria** dropdown. For **Search value**, add the search terms relevant to you. You may add multiple filters. If no filters are specified, Airbyte will replicate all data.
9. Click **Set up source** and wait for the tests to complete.

### Supported Objects

The Salesforce connector supports reading both Standard Objects and Custom Objects from Salesforce. Each object is read as a separate stream. See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

Airbyte fetches and handles all the possible and available streams dynamically based on:

* If the authenticated Salesforce user has the Role and Permissions to read and fetch objects

* If the object has the queryable property set to true. Airbyte can fetch only queryable streams via the API. If you don’t see your object available via Airbyte, check if it is API-accessible to the Salesforce user you authenticated with.

### Incremental Deletes

The Salesforce connector retrieves deleted records from Salesforce. For the streams which support it, a deleted record will be marked with the `isDeleted=true` value in the respective field.

### Syncing Formula Fields

The Salesforce connector syncs formula field outputs from Salesforce. If the formula of a field changes in Salesforce and no other field on the record is updated, you will need to reset the stream to pull in all the updated values of the field. 

For detailed information on supported sync modes, supported streams and performance considerations, refer to the 
[full documentation for Salesforce](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
