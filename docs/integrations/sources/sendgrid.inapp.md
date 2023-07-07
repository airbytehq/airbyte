## Prerequisites

* [Sendgrid API Key]((https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key)) with
  * Read-only access to all resources
  * Full access to marketing resources

## Setup guide

1. Enter a name for your Sendgridconnector.
2. Enter your `api key`.
3. (Optional) Enter the `start_time` in YYYY-MM-DDTHH:MM:SSZ format. Dataadded on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
4. Click **Set up source**.

### (Optional) Create a read-only API key

While you can set up the Sendgrid connector using any Salesforce user with read permission, we recommend creating a dedicated read-only user for Airbyte. This allows you to granularly control the which resources Airbyte can read.

The API key should be read-only on all resources except Marketing, where it needs Full Access.

Sendgrid provides two different kinds of marketing campaigns, "legacy marketing campaigns" and "new marketing campaigns". **Legacy marketing campaigns are not supported by this source connector**. 
If you are seeing a `403 FORBIDDEN error message for https://api.sendgrid.com/v3/marketing/campaigns`, it may be because your SendGrid account uses legacy marketing campaigns.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Sendgrid](https://docs.airbyte.com/integrations/sources/sendgrid).