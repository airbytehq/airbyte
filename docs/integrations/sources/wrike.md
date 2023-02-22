# Wrike 

This page guides you through the process of setting up the Wrike source connector.

## Prerequisites 

* Your [Wrike `Permanent Access Token`](https://help.wrike.com/hc/en-us/community/posts/211849065-Get-Started-with-Wrike-s-API)

## Set up the Wrike source connector 

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte OSS account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Wrike** from the Source type dropdown.
4. Enter a name for your source.
5. For **Permanent Access Token**, enter your [Wrike `Permanent Access Token`](https://help.wrike.com/hc/en-us/community/posts/211849065-Get-Started-with-Wrike-s-API).
    
    Permissions granted to the permanent token are equal to the permissions of the user who generates the token.

6. For **Wrike Instance (hostname)**, add the hostname of the Wrike instance you are currently using. This could be `www.wrike.com`, `app-us2.wrike.com`, or anything similar.
7. For **Start date for comments**, enter the date in `YYYY-MM-DDTHH:mm:ssZ` format. The comments added on and after this date will be replicated. If this field is blank, Airbyte will replicate comments from the last seven days.
8. Click **Set up source**.

## Supported sync modes

The Wrike source connector supports on full sync refresh.

## Supported Streams

The Wrike source connector supports the following streams:

* [Tasks](https://developers.wrike.com/api/v4/tasks/)\(Full Refresh\)
* [Customfields](https://developers.wrike.com/api/v4/customfields/)\(Full Refresh\)
* [Comments](https://developers.wrike.com/api/v4/comments/)\(Full Refresh\)
* [Contacts](https://developers.wrike.com/api/v4/contacts/)\(Full Refresh\)
* [Folders](https://developers.wrike.com/api/v4/folders/)\(Full Refresh\)

### Data type mapping

Currencies are number and the date is a string.

### Performance considerations

The Wrike connector should not run into Wrike API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.0   | 2022-08-16 | [15638](https://github.com/airbytehq/airbyte/pull/15638) | Initial version/release of the connector.

