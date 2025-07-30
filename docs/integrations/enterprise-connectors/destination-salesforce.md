---
dockerRepository: airbyte/destination-salesforce
---
# Salesforce Destination

## Overview

The Salesforce destination connector enables [data activation](elt-data-activation) by syncing data from your data warehouse to Salesforce objects. This connector is designed for operational workflows where you need to deliver modeled data directly to your CRM for sales, marketing, and customer success teams.

The connector uses the [Salesforce Bulk API v62.0](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm) for efficient data loading and supports OAuth 2.0 authentication with comprehensive error handling through Dead Letter Queue (DLQ) functionality.

### Key Features

- **Data Activation Support**: Sync enriched customer data, lead scores, and product usage metrics from your warehouse to Salesforce
- **Bulk API Integration**: Uses Salesforce Bulk API v62.0 for high-performance data loading with 100MB batch processing
- **Dead Letter Queue**: Failed records are automatically captured and stored in S3 for analysis and reprocessing
- **OAuth 2.0 Authentication**: Secure authentication with support for both sandbox and production environments
- **CSV Format Processing**: Data is processed in CSV format for optimal compatibility with Salesforce Bulk API

### Use Cases

- **Revenue Operations**: Sync product usage scores and engagement metrics to help sales reps prioritize high-intent accounts
- **Customer Success**: Deliver customer health scores and usage analytics to support teams for proactive outreach
- **Marketing Automation**: Push audience segments and behavioral data to enable targeted campaigns
- **Lead Scoring**: Sync calculated lead scores from your data warehouse to Salesforce for automated lead routing

## Prerequisites

- [Salesforce Account](https://login.salesforce.com/) with Enterprise edition or Professional edition with API access purchased
- Salesforce developer application with OAuth 2.0 credentials (Client ID and Client Secret)
- (Recommended) Dedicated Salesforce user with appropriate object permissions
- S3 bucket for Dead Letter Queue storage (optional but recommended)

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
   - **Callback URL**: `https://cloud.airbyte.com/auth/callback` (for Airbyte Cloud)
   - **Selected OAuth Scopes**: Add "Full access (full)" and "Perform requests on your behalf at any time (refresh_token, offline_access)"
6. Click **Save** and then **Continue**
7. Note the **Consumer Key** (Client ID) and **Consumer Secret** (Client Secret) for later use

### Step 2: (Recommended) Create a dedicated Salesforce user

Create a dedicated user with specific permissions for data synchronization to follow security best practices.

1. Navigate to **Setup** > **Users** > **Users**
2. Click **New User** and fill in the required fields:
   - Select **Salesforce Platform** for User License
   - Select **Standard Platform User** for Profile
3. Create a Permission Set for Airbyte:
   - Go to **Setup** > **Users** > **Permission Sets**
   - Click **New** and create a permission set named "Airbyte Data Sync"
   - Under **Object Settings**, grant the following permissions for each Salesforce object you want to sync to:
     - **Read**, **Create**, **Edit** permissions
     - **View All** and **Modify All** (if needed for your use case)
4. Assign the permission set to your dedicated user

### Step 3: Set up the Salesforce connector in Airbyte

<!-- env:cloud -->

## For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account
2. Click **Destinations** and then click **+ New destination**
3. Select **Salesforce** from the destination type dropdown
4. Enter a name for the Salesforce connector
5. Configure authentication:
   - **Client ID**: Enter the Consumer Key from your Connected App
   - **Client Secret**: Enter the Consumer Secret from your Connected App
   - **Refresh Token**: Click **Authenticate your account** to generate this automatically
   - **Is Sandbox**: Toggle this if you're connecting to a Salesforce sandbox environment
6. (Optional) Configure Dead Letter Queue:
   - **Object Storage Configuration**: Select **S3** to enable DLQ
   - Configure your S3 bucket details for storing failed records
7. Click **Set up destination** and wait for the connection test to complete

<!-- /env:cloud -->

## Configuration

### Authentication

The connector uses OAuth 2.0 with the following required fields:

- **Client ID**: The Consumer Key from your Salesforce Connected App
- **Client Secret**: The Consumer Secret from your Salesforce Connected App  
- **Refresh Token**: Generated through the OAuth flow when you authenticate your account
- **Is Sandbox**: Set to `true` if connecting to a Salesforce sandbox, `false` for production

### Dead Letter Queue (DLQ)

The connector supports Dead Letter Queue functionality to handle failed records:

- **Storage Type**: Currently supports S3 storage
- **Format**: Failed records are stored in CSV or JSONL format
- **Bucket Configuration**: Requires S3 bucket name, region, and access credentials
- **Path Format**: Configurable path structure for organizing failed records

Failed records include the original data plus error information to help with troubleshooting and reprocessing.

## Supported Sync Modes

The Salesforce destination currently supports:

- **Append**: Insert new records into Salesforce objects

:::info

While the underlying implementation supports additional operations (update, upsert, delete), only append mode is currently exposed through the connector specification. Contact support if you need additional sync modes for your use case.

:::

## Data Activation

This connector is specifically designed for [data activation](elt-data-activation) workflows. Common patterns include:

### Revenue Operations Example

1. **Source**: Customer usage data in your data warehouse (Snowflake, BigQuery, etc.)
2. **Transformation**: Calculate engagement scores and product adoption metrics
3. **Activation**: Sync these scores to custom fields in Salesforce Account or Contact objects
4. **Result**: Sales reps see real-time usage data in their CRM for better account prioritization

### Customer Success Example

1. **Source**: Product analytics and support ticket data in your warehouse
2. **Transformation**: Build customer health scores and risk indicators
3. **Activation**: Sync health scores to Salesforce for automated workflows
4. **Result**: Customer success teams get proactive alerts for at-risk accounts

## Limitations and Considerations

### Technical Limitations

- **Batch Size**: Maximum batch size is 100MB per upload to Salesforce Bulk API
- **API Version**: Uses Salesforce Bulk API v62.0
- **Format**: Data is processed in CSV format only
- **Sync Mode**: Currently limited to append operations

### Operational Considerations

- **API Limits**: Respect Salesforce API limits based on your edition and purchased API calls
- **Field Mapping**: Ensure source data types are compatible with target Salesforce field types
- **Object Permissions**: The authenticated user must have appropriate permissions on target objects
- **Bulk API Quotas**: Monitor your Bulk API usage as it counts against your daily limits

### Error Handling

- Failed records are captured and sent to the configured Dead Letter Queue
- Job status is monitored through polling with 5-second intervals
- Terminal job states include: JobComplete, Failed, and Aborted
- Detailed error information is available in DLQ records for troubleshooting

## Troubleshooting

### Authentication Issues

- **Invalid Client Credentials**: Verify your Connected App's Consumer Key and Consumer Secret
- **Refresh Token Expired**: Re-authenticate through the Airbyte UI to generate a new refresh token
- **Sandbox vs Production**: Ensure the "Is Sandbox" setting matches your Salesforce environment

### Permission Issues

- **Insufficient Object Permissions**: Verify the authenticated user has Create/Edit permissions on target objects
- **Field-Level Security**: Check that required fields are accessible to the user
- **API Access**: Confirm your Salesforce edition includes API access

### Data Issues

- **Batch Size Exceeded**: Large datasets may need to be split into smaller batches
- **Field Type Mismatches**: Ensure source data types are compatible with Salesforce field types
- **Required Field Validation**: Check that all required Salesforce fields are populated

### Monitoring

- Review sync logs in the Airbyte UI for detailed error messages
- Check the Dead Letter Queue in your S3 bucket for failed records
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
    "s3_bucket_name": "your-dlq-bucket",
    "s3_bucket_region": "us-east-1"
  }
}
```

## Related Documentation

- [Data Activation Overview](elt-data-activation)
- [Salesforce Bulk API Documentation](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_intro.htm)
- [Salesforce Connected Apps](https://help.salesforce.com/s/articleView?id=sf.connected_app_create.htm)
- [Rejected Records](rejected-records)

