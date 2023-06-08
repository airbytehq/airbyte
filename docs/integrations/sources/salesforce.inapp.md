## Prerequisites

* [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
* (Optional) Dedicated Salesforce [user](https://help.salesforce.com/s/articleView?id=adding_new_users.htm&type=5&language=en_US)

## Setup guide

1. Enter a name for the Salesforce connector.
2. Click **Authenticate your account** to authorize your Salesforce account. Airbyte will authenticate the Salesforce account you are already logged in to. Make sure you are logged into the right account. We recommend creating a dedicated read-only Salesforce user (see below for instructions).
3. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.
4. (Optional) Enter the **Start Date** in YYYY-MM-DDT00:00:00Z format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate the data for last two years.
5. (Optional) In the Salesforce Object filtering criteria section, click **Add**. From the Search criteria dropdown, select the criteria relevant to you. For Search value, add the search terms relevant to you. If this field is blank, Airbyte will scan for all objects. You can also filter which objects you want to sync later on when setting up your connection.
9. Click **Set up source**.

### (Optional) Create a read-only Salesforce user

While you can set up the Salesforce connector using any Salesforce user with read permission, we recommend creating a dedicated read-only user for Airbyte. This allows you to granularly control the data Airbyte can read.

To create a dedicated read only Salesforce user:

1. [Log into Salesforce](https://login.salesforce.com/) with an admin account.
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

### Supported Objects

The Salesforce connector supports reading both Standard Objects and Custom Objects from Salesforce. Each object is read as a separate stream. See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

Airbyte fetches and handles all the possible and available streams dynamically based on:

* If the authenticated Salesforce user has the Role and Permissions to read and fetch objects

* If the object has the queryable property set to true. Airbyte can fetch only queryable streams via the API. If you don’t see your object available via Airbyte, check if it is API-accessible to the Salesforce user you authenticated with in Step 2.

### Incremental Deletes

The Salesforce connector retrieves deleted records from Salesforce. For the streams which support it, a deleted record will be marked with the field `isDeleted=true` value.

### Syncing Formula Fields

The Salesforce connector syncs formula field outputs from Salesforce. If the formula of a field changes in Salesforce and no other field on the record is updated, you will need to reset the stream to pull in all the updated values of the field. 

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Salesforce](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
