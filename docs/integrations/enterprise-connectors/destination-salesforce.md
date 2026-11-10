---
dockerRepository: airbyte/destination-salesforce
enterprise-connector: true
---

# Salesforce destination

The Salesforce destination connector enables [data activation](/platform/move-data/elt-data-activation) by syncing data from your data warehouse to Salesforce objects. This connector is designed for operational workflows where you need to deliver modeled data directly to your CRM for sales, marketing, and customer success teams.

The connector uses the [Salesforce Bulk API v62.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm) for efficient data loading and supports OAuth 2.0 authentication with comprehensive error handling through [rejected records](/platform/move-data/rejected-records) functionality.

## Key features

- **Data Activation Support**: Sync enriched customer data, lead scores, and product usage metrics from your warehouse to Salesforce
- **Bulk API Integration**: Uses Salesforce Bulk API v62.0 for high-performance data loading with 100MB batch processing
- **Rejected Records**: Optionally store rejected records in S3 for analysis and reprocessing. Without object storage, Airbyte doesn't retain rejected record payloads.
- **OAuth 2.0 Authentication**: Secure authentication with support for both sandbox and production environments
- **CSV Format Processing**: Data is processed in CSV format for optimal compatibility with Salesforce Bulk API

## Prerequisites

- A [Salesforce account](https://login.salesforce.com/) with one of the following subscriptions:
    - Enterprise Edition
    - Unlimited Edition
    - Performance Edition
    - Developer Edition
    - Professional Edition with API access purchased as an add-on
- An Airbyte Pro or Enterprise Flex plan
- The **API Enabled** system permission for the Salesforce user who authenticates the destination
- Recommended: a dedicated Salesforce user with appropriate object permissions

### S3 prerequisites for rejected records

If you're using an S3 bucket to store rejected records, you also need the following.

1. Allow connections from Airbyte to your AWS S3/Minio S3 cluster (if they exist in separate VPCs).
2. [Enforce encryption of data in transit](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html#transit).
3. An S3 bucket with credentials, a Role ARN, or an instance profile with read/write permissions configured for the host (EC2, EKS).

    - These fields are always required:

      - **S3 Bucket Name**
      - **S3 Bucket Region**
      - **Prefix Path in the Bucket**

    - If you are using STS Assume Role, you must provide:

      - **Role ARN**

    - If you are using AWS credentials, you must provide:

      - **Access Key ID**
      - **Secret Access Key**

    - If you are using an Instance Profile, you may omit the Access Key ID, Secret Access Key, and Role ARN.

## Setup guide

### Step 1: Create a dedicated Salesforce user (optional but recommended)

Follow the instructions below to create a profile and assign custom permission sets to grant the new user the write access needed for data you want to access with Airbyte.

[Log in to Salesforce](https://login.salesforce.com/) with an admin account.

#### 1. Create a new User

- On the top right of the screen, click the gear icon and then click **Setup**.
- In the left navigation bar, under Administration, click **Users** > **Users**. Create a new User, entering details for the user's first name, last name, alias, and email. Filling in the email field auto-populates the username field and nickname.
      - Leave `role` unspecified
      - Select `Salesforce Platform` for the User License
      - Select `Standard Platform User` for Profile.
      - Decide whether to generate a new password and notify the user.
      - Select `save`

The Salesforce Platform license doesn't provide access to Leads, Opportunities, or Campaigns. To write to these objects, assign a full Salesforce license instead.

#### 2. Create a new permission set

- Using the left navigation bar, select **Users** > **Permission Sets**
- Click `New` to create a new Permission Set.
- Give your permission set a descriptive label name (e.g., "Airbyte Data Activation"). The API name will autopopulate based on the label you give the permission set.
- For licence, leave this set to `–None—` and click `save`.
- Now that you see the permission set is created, define the permissions via Object Settings.
   - Click "Object Settings."
   - Select the `Object Name` for each object you want the user to have write access to (e.g., Accounts, Contacts, Opportunities).
   - Click **Edit** and select the object permissions required for your write modes under **Object Permissions**:
     - **Create** for insert
     - **Edit** for update
     - **Create** and **Edit** for upsert. The target object must also have an external ID field for matching records. Upsert can't match on Salesforce's standard `Id` field.
     - **Delete** for delete
   - Grant **Read** on **Contact**, even if Contact isn't a target object. The connection check retrieves the Contact schema.
   - Grant edit access to the fields you map.
   - Click `Save`
   - Continue to add permissions for any objects you want Airbyte to have access to.

In the permission set's **System Permissions** section, enable **API Enabled**. Write modes the user doesn't have permission to use aren't selectable in Airbyte's mapping screen.

#### 3. Assign the permission set to the new user

- From the Permission Sets page, click **Manage Assignments** next to the permission set you just created.
- Click "Add Assignments."
- Find and select the user you created in Step 1.
- Click `Assign`

Log into the email you used in the preceding steps and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

:::info
**Profile vs. Permission Set**: remember that the user's profile provides their baseline permissions. The permission set adds or restricts permissions on top of that.
**Object-Level vs. Field-Level Security**: grant the object permissions required for your write modes and edit access to the fields you map.
:::

### Step 2: Set up the Salesforce connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud

Airbyte always uses its own Salesforce OAuth app and ignores any client ID or client secret you supply. Contact [Airbyte support](https://support.airbyte.com) if you need to use your own app. Syncs run as the Salesforce user who authenticates the destination.

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account
2. Click **Destinations** and then click **+ New destination**
3. Select **Salesforce** from the destination type dropdown
4. Enter a name for the Salesforce connector
5. Configure authentication:
   - **Is Sandbox**: First, toggle this setting based on your Salesforce environment (sandbox or production). **Note**: Changing this setting requires redoing authentication.
   - Click **Authenticate your account** and log in to Salesforce as the integration user.
6. Click **Set up destination** and wait for the connection test to complete

<!-- /env:cloud -->

## Configuration

The connector uses OAuth 2.0 authentication through Airbyte's Salesforce app. Make sure to set the **Is Sandbox** option correctly before authenticating, as this determines which Salesforce environment you connect to.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | No |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |
| Support [Namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces) | No |

## Limitations and considerations

- **API Limits**: respect Salesforce API limits based on your edition and purchased API calls
- **Field Mapping**: ensure source data types are compatible with target Salesforce field types
- **Object Permissions**: the authenticated user must have appropriate permissions on target objects
- **Bulk API Quotas**: monitor your Bulk API usage as it counts against your daily limits

### Error handling

- If you configure object storage, rejected record payloads are saved for troubleshooting.
- Monitor sync status through the Airbyte UI for detailed error information

## Troubleshooting

### Authentication issues

- **Uninstalled App Blocked**: Ask your Salesforce administrator to install Airbyte's app in your org and grant the integration user access. Salesforce restricts authorization of uninstalled apps; the **Approve Uninstalled Connected Apps** permission is intended only for highly trusted users. See [Salesforce's connected app authorization guidance](https://help.salesforce.com/s/articleView?id=005228838&language=en_US&type=1).
- **Refresh Token Expired**: Re-authenticate through the Airbyte UI to generate a new refresh token
- **Sandbox vs Production**: Ensure the "Is Sandbox" setting matches your Salesforce environment. Changing this setting requires redoing authentication.

### Permission issues

- **Insufficient Object Permissions**: Verify the authenticated user has Create/Edit permissions on target objects
- **Field-Level Security**: Check that required fields are accessible to the user
- **API Access**: Confirm your Salesforce edition includes API access

### Data issues

- **Field Type Mismatches**: Ensure source data types are compatible with Salesforce field types
- **Required Field Validation**: Check that all required Salesforce fields are populated

### Monitoring

- Review sync logs in the Airbyte UI for detailed error messages
- Monitor Salesforce Setup > System Overview for API usage and limits

## Reference

Set up and authenticate this destination in the Airbyte UI. The public API's `initiateOAuth` endpoint supports sources, not destinations, so you can't complete Salesforce destination authentication through the public API or Terraform. The connector specification requires `client_id`, `client_secret`, `refresh_token`, and `auth_type`, which the UI authentication flow supplies. The following JSON illustrates only the sandbox setting and optional S3 configuration; it isn't a complete configuration or a payload you can send to the API or Terraform:

```json
{
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

## Related documentation

- [Data Activation Overview](/platform/move-data/elt-data-activation)
- [Salesforce Bulk API Documentation](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm)
- [Rejected Records](/platform/move-data/rejected-records)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull request | Subject |
| :--- | :--- | :--- | :--- |
| 0.0.8 | 2025-09-26 | [240](https://github.com/airbytehq/airbyte-enterprise/pull/240) | Pin Salesforce connector dependencies. |
| 0.0.7 | 2025-09-15 | [226](https://github.com/airbytehq/airbyte-enterprise/pull/226) | Use a declarative specification. |
| 0.0.6 | 2025-07-30 | [209](https://github.com/airbytehq/airbyte-enterprise/pull/209) | Remove mandatory fields and fix discovery. |

</details>
