## Prerequisites

* A [Facebook Ad Account ID](https://www.facebook.com/business/help/1492627900875762)

## Setup guide

### For Airbyte Cloud:

**To set up Facebook Marketing as a source in Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Facebook Marketing** from the **Source type** dropdown.
4. For Name, enter a name for your Facebook Marketing connector.

**Facebook Marketing Source Settings:**

1. Click **Authenticate your account** to authorize your [Meta for Developers](https://developers.facebook.com/) account. Airbyte will authenticate the account you are already logged in to. Make sure you are logged into the right account.
2. Account ID: [Facebook Ad Account ID Number](https://www.facebook.com/business/help/1492627900875762): The Facebook Ad account ID to use when pulling data from the Facebook Marketing API. Open your Meta Ads Manager. The Ad account ID number is in the account dropdown menu or in your browser's address bar. See the [docs](https://www.facebook.com/business/help/1492627900875762) for more information. 
3. For **Start Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.

    :::warning
    Insight tables are only able to pull data from 37 months. If you are syncing insight tables and your start date is older than 37 months, your sync will fail.
    :::

4. For **End Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The date until which you'd like to replicate data for all incremental streams. All data generated between the start date and this end date will be replicated. Not setting this option will result in always syncing the latest data. 
5. For **Access Token**, if you don't use OAuth. [Generate Access Token:](https://docs.airbyte.com/integrations/sources/facebook-marketing). The value of the generated access token. From your App’s Dashboard, click on "Marketing API" then "Tools". Select permissions <b>ads_management, ads_read, read_insights, business_management</b>. Then click on "Get token". See the [docs](https://docs.airbyte.com/integrations/sources/facebook-marketing) for more information. 
6. For Account ID, enter your [Facebook Ad Account ID Number](https://www.facebook.com/business/help/1492627900875762): The Facebook Ad account ID to use when pulling data from the Facebook Marketing API. Open your Meta Ads Manager. The Ad account ID number is in the account dropdown menu or in your browser's address bar. See the [docs](https://www.facebook.com/business/help/1492627900875762) for more information.
7. (Optional) Toggle the **Include Deleted** button to include data from deleted Campaigns, Ads, and AdSets.

    :::info
    The Facebook Marketing API does not have a concept of deleting records in the same way that a database does. While you can archive or delete an ad campaign, the API maintains a record of the campaign. Toggling the **Include Deleted** button lets you replicate records for campaigns or ads even if they were archived or deleted from the Facebook platform.
    :::

8. (Optional) Toggle the **Fetch Thumbnail Images** button to fetch the `thumbnail_url` and store the result in `thumbnail_data_url` for each [Ad Creative](https://developers.facebook.com/docs/marketing-api/creative/).
9. (Optional) In the Custom Insights section. A list which contains ad statistics entries, each entry must have a name and can contain fields, breakdowns or action_breakdowns. Click on "add" to fill this field.
    To retrieve specific fields from Facebook Ads Insights combined with other breakdowns, you can choose which fields and breakdowns to sync.

    :::warning
    Additional streams for Facebook Marketing are dynamically created based on the specified Custom Insights. For an existing Facebook Marketing source, when you are updating or removing Custom Insights, you should also ensure that any connections syncing to these streams are either disabled or have had their source schema refreshed.
    :::

    We recommend following the Facebook Marketing [documentation](https://developers.facebook.com/docs/marketing-api/insights/breakdowns) to understand the breakdown limitations. Some fields can not be requested and many others only work when combined with specific fields. For example, the breakdown `app_id` is only supported with the `total_postbacks` field.

    To configure Custom Insights:

    1. For **Name**, enter a name for the insight. This will be used as the Airbyte stream name
    2. For **Fields**, enter a list of the fields you want to pull from the Facebook Marketing API.
    3. For **End Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and before this date will be replicated. If this field is blank, Airbyte will replicate the latest data.
    4. For **Breakdowns**, enter a list of the breakdowns you want to configure.
    5. For **Start Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
    6. For **Time Increment**, enter the number of days over which you want to aggregate statistics.

            For example, if you set this value to 7, Airbyte will report statistics as 7-day aggregates starting from the Start Date. Suppose the start and end dates are October 1st and October 30th, then the connector will output 5 records: 01 - 06, 07 - 13, 14 - 20, 21 - 27, and 28 - 30 (3 days only).  
    7. For **Action Breakdown**, enter a list of the action breakdowns you want to configure.
    8. For **Custom Insights Lookback Window**, fill in the appropriate value. See [more](#facebook-marketing-attribution-reporting) on this parameter.
    9. Click **Done**.
10. For **Page Size of Requests**, fill in the page size in case pagination kicks in. Feel free to ignore it, the default value should work in most cases. 
11. For **Insights Lookback Window**, fill in the appropriate value. Facebook freezes insight data 28 days after it was generated, which means that all data from the past 28 days may have changed since we last emitted it, so you can retrieve refreshed insights from the past by setting this parameter. If you set a custom lookback window value in Facebook account, please provide the same value here. See [more](#facebook-marketing-attribution-reporting) on this parameter. 
12. Click **Set up source**.
