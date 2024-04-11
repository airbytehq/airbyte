# NetSuite

This page contains the setup guide and reference information for NetSuite.

Daspire implements the [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html) and uses REST API to fetch the customers data.

## Prerequisites

* [Oracle NetSuite account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
* Allowed access to all Account permissions options
* Realm
* Consumer Key
* Consumer Secret
* Token ID
* Token Secret
* Language (the default language for your company)

## Setup guide

### Step 1: Setup NetSuite account and obtain required information

#### Step 1.1: Obtain Realm info

1. Login into your [NetSuite account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)

2. Go to **Setup** » **Company** » **Company Information**

3. Copy your **Account ID**. Your account ID is your Realm. It will looks like **1234567** if you use regular account or **1234567\_SB2** if it is a Sandbox
![NetSuite Realm](/docs/setup-guide/assets/images/netsuite-realm.jpg "NetSuite Realm")

#### Step 1.2: Enable features

1. Go to **Setup** » **Company** » **Enable Features**

2. Click on **SuiteCloud** tab

3. Scroll down to **Manage Authentication** section

4. Enable checkbox **TOKEN-BASED AUTHENTICATION**

5. Save changes
![NetSuite Token Based Auth](/docs/setup-guide/assets/images/netsuite-token-based-auth.jpg "NetSuite Token Based Auth")

#### Step 1.3: Create Integration (obtain Consumer Key and Consumer Secret)

1. Go to **Setup** » **Integration** » **Manage Integrations** » **New**

2. Fill the **Name** field. _It is a just description of integration_

3. **State** will keep **enabled**

4. Set up your **Concurrency limit**, and make sure it's equal or less than **concurrency limit**

5. Enable checkbox **Token-Based Authentication** on _Authentication_ section

6. Save changes

7. After that, **Consumer Key** and **Consumer Secret** will be showed once, copy them.
![NetSuite Integration](/docs/setup-guide/assets/images/netsuite-integration.jpg "NetSuite Integration")

#### Step 1.4: Setup Role

1. Go to **Setup** » **Users/Roles** » **Manage Roles** » **New**

2. Fill the **Name** field.

3. Scroll down to **Permissions** tab.

4. You need to select manually each record on selection lists and give **Full** level access on next tabs: (Permissions, Reports, Lists, Setup, Custom Records). You strongly need to be careful and attentive on this point.
![NetSuite Setup Role](/docs/setup-guide/assets/images/netsuite-setup-role.jpg "NetSuite Setup Role")

#### Step 1.5: Setup User

1. Go to **Setup** » **Users/Roles** » **Manage Users**

2. In column _Name_ click on the user's name you want to give access

3. Then click on **Edit** button under the user's name

4. Scroll down to **Access** tab at the bottom

5. Select from dropdown list the role which you created in step **1.4**

6. Save changes
![NetSuite Setup User](/docs/setup-guide/assets/images/netsuite-setup-user.jpg "NetSuite Setup User")

#### Step 1.6: Create Access Token for role

1. Go to **Setup** » **Users/Roles** » **Access Tokens** » **New**

2. Select an **Application Name**

3. Under **User** select the user you assigned the _Role_ in the step **1.4**

4. Inside **Role** select the one you gave to the user in the step **1.5**

5. Under **Token Name** you can give a descriptive name to the Token you are creating

6. Save changes

7. After that, **Token ID** and **Token Secret** will be showed once, copy them
![NetSuite Access Token](/docs/setup-guide/assets/images/netsuite-access-token.jpg "NetSuite Access Token")

#### Step 1.7: Obtain default language for your company

1. Go to **Setup** » **Setup Manager** » **Company** » **General Preference**

2. Click on **Languages** tab

3. You will find the default lanaguge for your company here
![NetSuite Default Company Language](/docs/setup-guide/assets/images/netsuite-default-company-language.jpg "NetSuite Default Company Language")

#### Step 1.8: Summary

You have obtained the following parameters:

* Realm (Account ID)
* Consumer Key
* Consumer Secret
* Token ID
* Token Secret 
* Default language for your company
* Also you have properly **Configured Account** with **Correct Permissions** and **Access Token** for User and Role you've created early.

### Step 2: Set up the source in Daspire

1. Go to Daspire dashboard.

2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.

3. On the source setup page, select **NetSuite** from the Source type dropdown and enter a name for this source.

4. Add **Realm**

5. Add **Consumer Key**

6. Add **Consumer Secret**

7. Add **Token ID**

8. Add **Token Secret**

9. Add **Language**

10. Add **Object Types**

11. Add **Start Date**

12. Click **Save & Test**

## Supported sync modes

The NetSuite source connector supports the following sync modes:

* Full Refresh
* Incremental

## Supported Streams

* Streams are generated based on ROLE and USER access to them as well as Account settings, make sure you're using Admin or any other custom ROLE granted to the Access Token, having the access to the NetSuite objects for data sync.

## Performance considerations

1. The integration is restricted by Netsuite [Concurrency Limit per Integration](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html). Sync might stop or fail if Concurrency Limit is reached. 

  > You can find your Concurrency Limit per Integration in **Setup** » **Integration** » **Integration Goverance**. Under **Concurrency Usage** you can view the account concurrency limit and the unallocated concurrency limit.

2. If sync fails due to concurrency limit, you can try resync to see if it works.

3. You can also contact NetSuite customer support to [change your Concurrency Limits](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_164095787873.html#:~:text=By%20default%2C%20NetSuite%20Connector%20limits,limit%2C%20contact%20NetSuite%20Customer%20Support).

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.