# Oracle Netsuite

One unified business management suite, encompassing ERP/Financials, CRM and ecommerce for more than 31,000 customers.

This connector implements the [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html) and uses REST API to fetch the customers data.

## Prerequisites
* Oracle NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
* Allowed access to all Account permissions options

## Airbyte OSS and Airbyte Cloud
* Realm
* Consumer Key
* Consumer Secret
* Token ID
* Token Secret

## Setup guide
### Step 1: Create NetSuite account

1. Create [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US) on Oracle NetSuite
2. Confirm your Email

### Step 2: Setup NetSuite account
#### Step 2.1: Obtain Realm info
1. Login into your NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
2. Go to **Setup** » **Company** » **Company Information**
3. Copy your Account ID. It will looks like **1234567** if you use regular account or **1234567_SB2** if it is a Sandbox
#### Step 2.2: Enable features
1. Go to **Setup** » **Company** » **Enable Features**
2. Click on **SuiteCloud** tab
3. Scroll down to **Manage Authentication** section
4. Enable checkbox **TOKEN-BASED AUTHENTICATION**
5. Save changes
#### Step 2.3: Create Integration (obtain Consumer Key and Consumer Secret)
1. Go to **Setup** » **Integration** » **Manage Integrations** » **New**
2. Fill the **Name** field. *It is a just description of integration*
3. **State** will keep **enabled**
4. Enable checkbox **Token-Based Authentication**  on *Authentication* section
5. Save changes
6. After that, **Consumer Key** and **Consumer Secret** will be showed once, copy them.
#### Step 2.4:  Setup Role
1. Go to **Setup** » **Users/Roles** » **Manage Roles** » **New**
2. Fill the **Name** field.
3. Scroll down to **Permissions** tab
4. You need to select manually each record on selection lists and give at least **Read-only** level access on the next tabs: (Permissions, Reports, Lists, Setup, Custom Records). You strongly need to be careful and attentive on this point.
5.
#### Step 2.5:  Setup User
1.  Go to **Setup** » **Users/Roles** » **Manage Users**
2.  In column _Name_ click on the user’s name you want to give access
3.  Then click on **Edit** button under the user’s name
4. Scroll down to **Access** tab at the bottom
5. Select from dropdown list the role which you created in step 2.4
6. Save changes

#### Step 2.6: Create Access Token for role
1. Go to **Setup** » **Users/Roles** » **Access Tokens** » **New**
2. Select an **Application Name**
3.  Under **User** select the user you assigned the _Role_ in the step **2.4**
4.  Inside **Role** select the one you gave to the user in the step **2.5**
5.  Under **Token Name** you can give a descriptive name to the Token you are creating
6.  Save changes
7. After that, **Token ID** and **Token Secret** will be showed once, copy them.

#### Step 2.7: Summary
You have copied next parameters
* Realm  (Account ID)
* Consumer Key
* Consumer Secret
* Token ID
* Token Secret
Also you have properly **Configured Account** with **Correct Permissions** and **Access Token** for User and Role you've created early.

### Step 3: Set up the source connector in Airbyte
### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **NetSuite** from the Source type dropdown and enter a name for this connector.
4. Add **Realm**
5. Add **Consumer Key**
6. Add **Consumer Secret**
7. Add **Token ID**
8. Add **Token Secret**
9. Click `Set up source`.

### For Airbyte OSS:

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **NetSuite** from the Source type dropdown and enter a name for this connector.
4. Add **Realm**
5. Add **Consumer Key**
6. Add **Consumer Secret**
7. Add **Token ID**
8. Add **Token Secret**
9. Click `Set up source`


## Supported sync modes

The NetSuite source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental

## Supported Streams

- Streams are generated based on `ROLE` and `USER` access to them as well as `Account` settings, make sure you're using `Admin` or any other custom `ROLE` granted to the Access Token, having the access to the NetSuite objects for data sync.


## Performance considerations

The connector is restricted by Netsuite [Concurrency Limit per Integration](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html).

## Changelog

| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.1   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state |
| 0.1.0   | 2022-09-15 | [16093](https://github.com/airbytehq/airbyte/pull/16093) | Initial Alpha release       |
