# Salesforce

This page contains the setup guide and reference information for Salesforce.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh - Overwrite | Yes |
| Full Refresh - Append | Yes |
| Incremental - Append | Yes |
| Incremental - Append + Deduped | Yes - recommended |

## Prerequisites

* Salesforce account with Enterprise access or API quota purchased
* (Optional but recommended) A dedicated Salesforce user
* Salesforce OAuth credentials (Client ID, Client Secret, Refresh Token)

Note: To use this integration, you'll need at least the **Enterprise edition** of Salesforce or the **Professional Edition with API access** purchased as an add-on. Reference the [Salesforce docs about API access](https://help.salesforce.com/s/articleView?id=000385436&type=1) for more information.

## Setup guide

### Step 1: (Optional, recommended) Create a read-only Salesforce user

1. [Log in to Salesforce](https://login.salesforce.com/) with an admin account.

2. On the top right of the screen, click the gear icon and then click **Setup**.

3. In the left navigation bar, under **Administration**, click **Users > Profiles**.

4. Click **New profile**.

5. For Existing Profile, select **Read only**. For Profile Name, enter **Daspire Read Only User**. Click Save.

6. The Profiles page is displayed. Click **Edit**.

7. Scroll down to the **Standard Object Permissions** and **Custom Object Permissions** and enable the **Read** checkbox for objects that you want to replicate via Daspire. Then scroll to the top and click Save.

8. On the left side, under **Administration**, click **Users > Users**. The All Users page is displayed.

9. Click **New User**. And fill out the required fields:
  > * For License, select **Salesforce**.
  > * For Profile, select **Daspire Read Only User**.
  > * For Email, make sure to use an email address that you can access.

10. Click Save. Then copy the **Username** and keep it accessible.

11. Log into the email you used above and verify your new Salesforce account user. You'll need to set a password as part of this process. Keep this password accessible.

### Step 2: Obtain Salesforce OAuth credentials

To obtain the Salesforce OAuth credentials, including Client ID, Client Secret, and Refresh Token, follow [this guide](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) with the following modifications:

1. If your Salesforce URL is not in the `X.salesforce.com` format, use your Salesforce domain name. For example, if your Salesforce URL is `mycompany.force.com` then use that instead of `mycompany.salesforce.com`.

2. When running a curl command, run it with the `-L` option to follow any redirects.

3. If you created a read-only user in Step 1, use the user credentials when logging in to generate OAuth tokens.

### Step 3: Set up Salesforce in Daspire

1. Select **Salesforce** from the Source list.

2. Enter a **Source Name**.

3. To authenticate, enter your **Client ID**, **Client Secret**, and **Refresh Token**.

4. Toggle whether your Salesforce account is a [Sandbox account](https://help.salesforce.com/s/articleView?id=sf.deploy_sandboxes_parent.htm&type=5) or a production account.

4. (Optional) For **Start Date**, enter the date in either `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ` format. The data added on and after this date will be replicated. If this field is left blank, Daspire will replicate the data for the last two years by default. Please note that timestamps are in UTC.

5. (Optional) In the **Filter Salesforce Object** section, you may choose to target specific data for replication. To do so, click **Add**, then select the relevant criteria from the **Search criteria** dropdown. For **Search value**, add the search terms relevant to you. You may add multiple filters. If no filters are specified, Daspire will replicate all data.

6. Click **Save & Test**.

## Supported Objects

The Salesforce integration supports reading both **Standard Objects** and **Custom Objects** from Salesforce. Each object is read as a separate stream. See a list of all Salesforce Standard Objects [here](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_list.htm).

Daspire allows exporting all available Salesforce objects dynamically based on:

* If the authenticated Salesforce user has the **Role** and **Permissions** to read and fetch objects

* If the salesforce object has the queryable property set to true. Daspire can only fetch objects which are queryable. If you don’t see an object available via Daspire, and it is queryable, check if it is API-accessible to the Salesforce user you authenticated with.

### BULK API vs REST API and their limitations

Salesforce allows extracting data using either the [BULK API](https://developer.salesforce.com/docs/atlas.en-us.236.0.api_asynch.meta/api_asynch/asynch_api_intro.htm) or [REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm). To achieve fast performance, Salesforce recommends using the **BULK API** for extracting larger amounts of data (more than 2,000 records). For this reason, the Daspire Salesforce integration uses the BULK API by default to extract any Salesforce objects, unless any of the following conditions are met:

* The Salesforce object has columns which are unsupported by the BULK API, like columns with a `base64` or `complexvalue` type
* The Salesforce object is not supported by BULK API. In this case we sync the objects via the REST API which will occasionalyl cost more of your API quota. This list of objects was obtained experimentally, and includes the following objects:

  * AcceptedEventRelation
  * Attachment
  * CaseStatus
  * ContractStatus
  * DeclinedEventRelation
  * FieldSecurityClassification
  * KnowledgeArticle
  * KnowledgeArticleVersion
  * KnowledgeArticleVersionHistory
  * KnowledgeArticleViewStat
  * KnowledgeArticleVoteStat
  * OrderStatus
  * PartnerRole
  * RecentlyViewed
  * ServiceAppointmentStatus
  * ShiftStatus
  * SolutionStatus
  * TaskPriority
  * TaskStatus
  * UndecidedEventRelation

More information on the differences between various Salesforce APIs can be found [here](https://help.salesforce.com/s/articleView?id=sf.integrate_what_is_api.htm&type=5).

**FORCE USING BULK API**: If you set the Force Use Bulk API option to **true**, the integration will ignore unsupported properties and sync Stream using BULK API.

### Incremental deletes sync

The Salesforce integration supports retrieving deleted records from the Salesforce recycle bin.

For the streams which support it, a deleted record will be marked with `isDeleted=true`. To find out more about how Salesforce manages records in the recycle bin, please visit their [docs](https://help.salesforce.com/s/articleView?id=sf.home_delete.htm&type=5).

## Performance considerations

The Salesforce integration is restricted by Salesforce’s [Daily Rate Limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm).

The integration syncs data until it hits the daily rate limit, then ends the sync early with success status, and starts the next sync from where it left off. Note that picking up from where it ends will work only for **incremental sync**, which is why we recommend using the **Incremental Sync - Append + Deduped** sync mode.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
