# Oracle Netsuite

One unified business management suite, encompassing ERP/Financials, CRM and ecommerce for more than 31,000 customers.

This connector implements the [SuiteAnalytics Connect Service](https://www.netsuite.com/portal/products/analytics.shtml) and uses an ODBC to fetch requested data.

## Prerequisites

- Oracle NetSuite Admin [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
- Netsuite SuiteAnalytics Connect (This is an additional service on top of the standard Netsuite license)

### Required Input Fields for Airbyte OSS and Airbyte Cloud

- Account ID
- Consumer Key
- Consumer Secret
- Token ID
- Token Secret
- Role ID (Of Data Warehouse Integrator Role)

## Setup guide

1. Netsuite Admin Account
2. Suite Analytics Connect Service Enabled with Access to netsuite2.com datasource

### Step 1: Make Sure You Have the Prerequisites

1. If you don't have access to an admin account, contact your Netsuite Admin
2. If you don't have access to SuiteAnalytics Connect (which you can determine by whether or not **Setup SuiteAnalytics Connect** shows up on your Homepage), contact your Netsuite Account Executive

### Step 2: Setup NetSuite account

#### Step 2.1: Obtain SuiteAnalytics Information (Host, Port, and Account ID)

1. Login into your NetSuite [account](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
2. From your Home Dashboard, find the **Settings** section and click on **Setup SuiteAnalytics Connect**
3. Copy and save your Service Host, Service Port, and Account ID
4. Service Host should look something like "XXXXXX.connect.api.netsuite.com". If it is a sandbox instance, you will see a "-sbX" at the end of the first sub-domain
5. Service Port should be a four digit number
6. Account ID should be a six digit number. If you're using a sandbox instance, it will be appended with a "\_SBX", where X is a digit

#### Step 2.2: Enable Token Based Authentication

1. Go to **Setup** » **Company** » **Enable Features**
2. Click on **SuiteCloud** tab
3. Scroll down to **SuiteScript** section
4. Enable the checkbox for `CLIENT SUITESCRIPT` and `SERVER SUITESCRIPT`
5. Scroll down to **Manage Authentication** section
6. Enable the checkbox for `TOKEN-BASED AUTHENTICATION`
7. Save the changes

#### Step 2.3: Create Integration Record

1. Go to **Setup** » **Integration** » **Manage Integrations** » **New**
2. Fill in the **Name** field (we recommend using something memorable like 'Airbyte ODBC Integration')
3. Make sure the **State** is `enabled`
4. Enable checkbox `Token-Based Authentication` in **Authentication** section. Make sure everything is NOT checked, as it can cause the connector to fail
5. Save changes
6. After that, **Consumer Key** and **Consumer Secret** will be showed at the bottom of the page. Copy these and save them somewhere safe. **They will only be shown once**

#### Step 2.4: Setup Your Suite Analytics Role

1. Go to **Setup** » **Users/Roles** » **Manage Roles** » **New**
2. Fill in the **Name** field (we recommend using something memorable like 'Airbyte ODBC Role')
3. Scroll down to **Permissions** tab
4. Click on `Setup` and manually add the `Log In Using Access Tokens` and `SuiteAnalytics Connect` permissions
5. Click Save

#### Step 2.5: Setup User

1. Go to **Setup** » **Users/Roles** » **Manage Users**
2. Decide which user you want to give permissions to
3. In column `Name` click on the user’s name
4. Then click on **Edit** button under the user’s name
5. Scroll down to **Access** tab at the bottom
6. Make sure the `Give Access` checkbox is enabled
7. In the **Roles** section select the `Data Warehouse Integrator Role`
8. In the **Roles** section select the dedicated SuiteAnalytics role you created in step 2.4
9. Click Save

#### Step 2.6: Create Access Token for role

1. Go to **Setup** » **Users/Roles** » **Access Tokens** » **New**
2. In the **Application Name** input, select the Integration Record you created in step 2.3
3. Under **User** select the user you assigned roles to in step **2.5**
4. Inside **Role** select the Data Warehouse Integrator Role
5. Under **Token Name**, you should provide a descriptive name to the Token you are creating
6. Save changes
7. After that, **Token ID** and **Token Secret** will be showed at the bottom of the page. Copy these and save them somewhere safe. **They will only be shown once.**

8. Get Data Warehouse integrator Role ID
   1. Set up -> Users/Roles -> Manage Roles
   2. Find the internal ID of the Data Warehouse Integrator role

#### Step 2.7: Get the Data Warehouse Integrator Role ID

1. Go to **Setup** » **Users/Roles** » **Manage Roles**
2. Find the internal ID of the Data Warehouse Integrator role. Copy and save it

### Step 3: Make Sure You Have the required Information

Before moving forward, you should check to see that you have:

- Service Host
- Service Port
- Account ID
- Consumer ID
- Consumer Secret
- Token ID
- Token Secret
- Date Warehouse Integrator Role ID

You should also have a correctly configured User with permissions to access Suite Analytics Connect

### Step 4: Set up the source connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Netsuite ODBC** from the Source type dropdown and enter a name for this connector.
4. Add **Account ID**
5. Add **Consumer Key**
6. Add **Consumer Secret**
7. Add **Token ID**
8. Add **Token Secret**
9. Add **Service Host**
10. Add **Service Port**
11. Add **Role ID** (Of Data Warehouse Integrator Role)
12. Click `Set up source`.

### For Airbyte OSS:

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **NetSuite ODBC** from the Source type dropdown and enter a name for this connector.
4. Add **Account ID**
5. Add **Consumer Key**
6. Add **Consumer Secret**
7. Add **Token ID**
8. Add **Token Secret**
9. Add **Service Host**
10. Add **Service Port**
11. Add **Role ID** (Of Data Warehouse Integrator Role)
12. Click `Set up source`

## Supported sync modes

The NetSuite source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

- Streams are generated based on `ROLE` and `USER` access to them, make sure you're using the correct role (see Step **2** to configure the role correctly)

## Performance considerations

The connector is restricted by Netsuite [Concurrency Limit per Integration](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html).

## Changelog

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
