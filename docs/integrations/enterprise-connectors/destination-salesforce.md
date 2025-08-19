---
dockerRepository: airbyte/destination-salesforce
---
# Salesforce Destination

The Salesforce destination connector enables [data activation](/platform/next/move-data/elt-data-activation) by syncing data from your data warehouse to Salesforce objects. This connector is designed for operational workflows where you need to deliver modeled data directly to your CRM for sales, marketing, and customer success teams.

:::info
Data activation is in early access. If you'd like to be an early adopter for this connector, [fill out this form](https://form.typeform.com/to/STc7a0jx).
:::

The connector uses the [Salesforce Bulk API v62.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm) for efficient data loading and supports OAuth 2.0 authentication with comprehensive error handling through [rejected records](/platform/next/move-data/rejected-records) functionality.

### Key Features

- **Data Activation Support**: Sync enriched customer data, lead scores, and product usage metrics from your warehouse to Salesforce
- **Bulk API Integration**: Uses Salesforce Bulk API v62.0 for high-performance data loading with 100MB batch processing
- **Rejected Records**: Failed records are automatically captured and stored in S3 for analysis and reprocessing
- **OAuth 2.0 Authentication**: Secure authentication with support for both sandbox and production environments
- **CSV Format Processing**: Data is processed in CSV format for optimal compatibility with Salesforce Bulk API


## Prerequisites

- [Salesforce Account](https://login.salesforce.com/) with Enterprise access or API quota purchased
- A version of the Airbyte platform to be at least 1.8 or cloud
- Salesforce developer application with OAuth 2.0 credentials (Client ID and Client Secret)
- (Recommended) Dedicated Salesforce user with appropriate object permissions

:::tip

To use this connector, you'll need at least the Enterprise edition of Salesforce or the Professional Edition with API access purchased as an add-on. Reference the [Salesforce docs about API access](https://help.salesforce.com/s/articleView?id=000385436&type=1) for more information.

:::

## Setup guide

### Step 1: Create a Salesforce Connected App

Before setting up the Airbyte connector, you need to create a Connected App in Salesforce to obtain OAuth 2.0 credentials.

1. Log in to your Salesforce org as an administrator
2. Navigate to **Setup** > **App Manager**
3. Click **New Connected App**
4. Fill in the basic information:
   - **Connected App Name**: "Airbyte Data Sync" (or your preferred name)
   - **API Name**: Will auto-populate
   - **Contact Email**: Your email address
5. Enable OAuth Settings:
   - Check **Enable OAuth Settings**
   - **Callback URL**: `https://cloud.airbyte.com/auth/callback` (for Airbyte Cloud) or `https://your-airbyte-domain.com/auth/callback` (for self-managed Airbyte)
   - **Selected OAuth Scopes**: Add "Full access (full)" and "Perform requests on your behalf at any time (refresh_token, offline_access)"
6. Click **Save** and then **Continue**
7. Note the **Consumer Key** (Client ID) and **Consumer Secret** (Client Secret) for later use

### Step 2: (Optional, Recommended) Create a dedicated Salesforce user

Follow the instructions below to create a profile and assign custom permission sets to grant the new user the write access needed for data you want to access with Airbyte.

[Log in to Salesforce](https://login.salesforce.com/) with an admin account.

#### 1. Create a new User:
-  On the top right of the screen, click the gear icon and then click **Setup**.
-  In the left navigation bar, under Administration, click **Users** > **Users**. Create a new User, entering details for the user's first name, last name, alias, and email. Filling in the email field will auto-populate the username field and nickname.
      - Leave `role` unspecified
      - Select `Salesforce Platform` for the User License
      - Select `Standard Platform User` for Profile.
      - Decide whether to generate a new password and notify the user.
      - Select `save`
#### 2. Create a new Permission Set:
-  Using the left navigation bar, select **Users** > **Permission Sets**
- Click `New` to create a new Permission Set.
- Give your permission set a descriptive label name (e.g., "Airbyte Data Activation"). The API name will autopopulate based on the label you give the permission set.
- For licence, leave this set to` –None—` and click `save`.
- Now that you see the permission set is created, define the permissions via Object Settings.
   - Click "Object Settings."
   - Select the `Object Name` for each object you want the user to have write access to (e.g., Accounts, Contacts, Opportunities).
   - Select "Edit" and check all the object permissions under "Object Permissions"
   - Click `Save`
   - Continue to add permissions for any objects you want Airbyte to have access to.
#### 3. Assign the Permission Set to the new User
- From the Permission Sets page, click "Manage Assignments" next to the read-only permission set you just created.
- Click "Add Assignments."
- Find and select the user you created in Step 1.
- Click `Assign`

Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

:::info
**Profile vs. Permission Set:** Remember that the user's profile will provide their baseline permissions. The permission set adds or restricts permissions on top of that.
**Object-Level vs. Field-Level Security:** This guide focuses on object-level read-only access. While setting up your permission set, you can stick with object-level security or define more granular controls by scrolling down within each object settings page to select read access for only needed fields.
:::

### Step 3: Set up the Salesforce connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account
2. Click **Destinations** and then click **+ New destination**
3. Select **Salesforce** from the destination type dropdown
4. Enter a name for the Salesforce connector
5. Configure authentication:
   - **Is Sandbox**: First, toggle this setting based on your Salesforce environment (sandbox or production). **Note**: Changing this setting requires redoing authentication.
   - **Client ID**: Enter the Consumer Key from your Connected App
   - **Client Secret**: Enter the Consumer Secret from your Connected App
   - **Refresh Token**: Click **Authenticate your account** to generate this automatically
6. Click **Set up destination** and wait for the connection test to complete

<!-- /env:cloud -->

<!-- env:oss -->

#### For Self-Managed Airbyte:

1. Navigate to your Airbyte instance (e.g., `http://localhost:8000`)
2. Click **Destinations** and then click **+ New destination**
3. Select **Salesforce** from the destination type dropdown
4. Enter a name for the Salesforce connector
5. Configure authentication:
   - **Is Sandbox**: First, set to `true` if connecting to a Salesforce sandbox, `false` for production. **Note**: Changing this setting requires redoing authentication.
   - **Client ID**: Enter the Consumer Key from your Connected App
   - **Client Secret**: Enter the Consumer Secret from your Connected App
   - **Refresh Token**: You'll need to obtain this through the OAuth flow using your callback URL
6. Click **Set up destination** and wait for the connection test to complete

<!-- /env:oss -->

## Configuration

The connector uses OAuth 2.0 authentication with your Salesforce Connected App credentials. Make sure to set the **Is Sandbox** option correctly before authenticating, as this determines which Salesforce environment you connect to.

## Supported Sync Modes

The Salesforce destination currently supports:

- **Append**: Insert new records into Salesforce objects

:::info

While the underlying implementation supports additional operations (update, upsert, delete), only append mode is currently exposed through the connector specification. Contact support if you need additional sync modes for your use case.

:::


## Limitations and Considerations

- **API Limits**: Respect Salesforce API limits based on your edition and purchased API calls
- **Field Mapping**: Ensure source data types are compatible with target Salesforce field types
- **Object Permissions**: The authenticated user must have appropriate permissions on target objects
- **Bulk API Quotas**: Monitor your Bulk API usage as it counts against your daily limits

### Error Handling

- Failed records are automatically captured for troubleshooting
- Monitor sync status through the Airbyte UI for detailed error information

## Troubleshooting

### Authentication Issues

- **Invalid Client Credentials**: Verify your Connected App's Consumer Key and Consumer Secret
- **Refresh Token Expired**: Re-authenticate through the Airbyte UI to generate a new refresh token
- **Sandbox vs Production**: Ensure the "Is Sandbox" setting matches your Salesforce environment. Changing this setting requires redoing authentication.

### Permission Issues

- **Insufficient Object Permissions**: Verify the authenticated user has Create/Edit permissions on target objects
- **Field-Level Security**: Check that required fields are accessible to the user
- **API Access**: Confirm your Salesforce edition includes API access

### Data Issues

- **Field Type Mismatches**: Ensure source data types are compatible with Salesforce field types
- **Required Field Validation**: Check that all required Salesforce fields are populated

### Monitoring

- Review sync logs in the Airbyte UI for detailed error messages
- Monitor Salesforce Setup > System Overview for API usage and limits

## Reference

For programmatic configuration, use these parameter names:

```json
{
  "client_id": "your_consumer_key",
  "client_secret": "your_consumer_secret", 
  "refresh_token": "your_refresh_token",
  "is_sandbox": false,
  "object_storage_config": {
    "storage_type": "S3",
    "access_key_id": "your_access_key_id",
    "secret_access_key": "your_secret_access_key",
    "s3_bucket_name": "your_bucket_name",
    "s3_bucket_region": "us-east-1",
    "bucket_path": "rejected_records/"
  }
}
```

## Related Documentation

- [Data Activation Overview](/platform/next/move-data/elt-data-activation)
- [Salesforce Bulk API Documentation](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm)
- [Salesforce Connected Apps](https://help.salesforce.com/s/articleView?id=sf.connected_app_create.htm)
- [Rejected Records](/platform/next/move-data/rejected-records)

