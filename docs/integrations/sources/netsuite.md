# Oracle Netsuite

One unified business management suite, encompassing ERP/Financials, CRM and ecommerce for more than 31,000 customers.

This connector implements the [SuiteTalk REST Web Services](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html) and uses REST API to fetch the customers data.

## Prerequisites

- Oracle NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
- Allowed access to all Account permissions options

## Airbyte OSS and Airbyte Cloud

- Realm (Account ID)
- Consumer Key
- Consumer Secret
- Token ID
- Token Secret

## Setup guide

### Step 1: Create NetSuite account

1. Create [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US) on Oracle NetSuite
2. Confirm your Email

### Step 2: Setup NetSuite account

#### Step 2.1: Obtain Realm info

1. Login into your NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
2. Go to **Setup** » **Company** » **Company Information**
3. Copy your Account ID (Realm). It should look like **1234567** for the `Production` env. or **1234567_SB2** - for a `Sandbox`

#### Step 2.2: Enable features

1. Go to **Setup** » **Company** » **Enable Features**
2. Click on **SuiteCloud** tab
3. Scroll down to **SuiteScript** section
4. Enable checkbox for `CLIENT SUITESCRIPT` and `SERVER SUITESCRIPT`
5. Scroll down to **Manage Authentication** section
6. Enable checkbox `TOKEN-BASED AUTHENTICATION`
7. Scroll down to **SuiteTalk (Web Services)**
8. Enable checkbox `REST WEB SERVISES`
9. Save the changes

#### Step 2.3: Create Integration (obtain Consumer Key and Consumer Secret)

1. Go to **Setup** » **Integration** » **Manage Integrations** » **New**
2. Fill the **Name** field (we recommend to put `airbyte-rest-integration` for a name)
3. Make sure the **State** is `enabled`
4. Enable checkbox `Token-Based Authentication` in **Authentication** section
5. Save changes
6. After that, **Consumer Key** and **Consumer Secret** will be showed once (copy them to the safe place)

#### Step 2.4: Setup Role

1. Go to **Setup** » **Users/Roles** » **Manage Roles** » **New**
2. Fill the **Name** field (we recommend to put `airbyte-integration-role` for a name)
3. Scroll down to **Permissions** tab
4. (REQUIRED) Click on `Transactions` and manually `add` all the dropdown entities with either `full` or `view` access level.
5. (REQUIRED) Click on `Reports` and manually `add` all the dropdown entities with either `full` or `view` access level.
6. (REQUIRED) Click on `Lists` and manually `add` all the dropdown entities with either `full` or `view` access level.
7. (REQUIRED) Click on `Setup` and manually `add` all the dropdown entities with either `full` or `view` access level.

- Make sure you've done all `REQUIRED` steps correctly, to avoid sync issues in the future.
- Please edit these params again when you `rename` or `customise` any `Object` in Netsuite for `airbyte-integration-role` to reflect such changes.

#### Step 2.5: Setup User

1. Go to **Setup** » **Users/Roles** » **Manage Users**
2. In column `Name` click on the user’s name you want to give access to the `airbyte-integration-role`
3. Then click on **Edit** button under the user’s name
4. Scroll down to **Access** tab at the bottom
5. Select from dropdown list the `airbyte-integration-role` role which you created in step 2.4
6. Save changes

#### Step 2.6: Create Access Token for role

1. Go to **Setup** » **Users/Roles** » **Access Tokens** » **New**
2. Select an **Application Name**
3. Under **User** select the user you assigned the `airbyte-integration-role` in the step **2.4**
4. Inside **Role** select the one you gave to the user in the step **2.5**
5. Under **Token Name** you can give a descriptive name to the Token you are creating (we recommend to put `airbyte-rest-integration-token` for a name)
6. Save changes
7. After that, **Token ID** and **Token Secret** will be showed once (copy them to the safe place)

#### Step 2.7: Summary

You have copied next parameters

- Realm (Account ID)
- Consumer Key
- Consumer Secret
- Token ID
- Token Secret
  Also you have properly **Configured Account** with **Correct Permissions** and **Access Token** for User and Role you've created early.

### Step 3: Set up the source connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
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

- Streams are generated based on `ROLE` and `USER` access to them as well as `Account` settings, make sure you're using the correct role assigned in our case `airbyte-integration-role` or any other custom `ROLE` granted to the Access Token, having the access to the NetSuite objects for data sync, please refer to the **Setup guide** > **Step 2.4** and **Setup guide** > **Step 2.5**

## Performance considerations

The connector is restricted by Netsuite [Concurrency Limit per Integration](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                   |
|:--------|:-----------| :------------------------------------------------------- |:----------------------------------------------------------|
| 0.1.10 | 2025-03-08 | [55455](https://github.com/airbytehq/airbyte/pull/55455) | Update dependencies |
| 0.1.9 | 2025-03-05 | [55207](https://github.com/airbytehq/airbyte/pull/55207) | Add support for additional date format in Netsuite input |
| 0.1.8 | 2025-03-01 | [54821](https://github.com/airbytehq/airbyte/pull/54821) | Update dependencies |
| 0.1.7 | 2025-02-22 | [54363](https://github.com/airbytehq/airbyte/pull/54363) | Update dependencies |
| 0.1.6 | 2025-02-15 | [53853](https://github.com/airbytehq/airbyte/pull/53853) | Update dependencies |
| 0.1.5 | 2025-02-08 | [53243](https://github.com/airbytehq/airbyte/pull/53243) | Update dependencies |
| 0.1.4 | 2024-07-29 | [42857](https://github.com/airbytehq/airbyte/pull/42857) | Migrate connector to Poetry |
| 0.1.3 | 2023-01-20 | [21645](https://github.com/airbytehq/airbyte/pull/21645) | Minor issues fix, Setup Guide corrections for public docs |
| 0.1.1 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state |
| 0.1.0 | 2022-09-15 | [16093](https://github.com/airbytehq/airbyte/pull/16093) | Initial Alpha release |

</details>
