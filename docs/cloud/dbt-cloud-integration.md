# Using the dbt Cloud integration

## Step 1: Prerequisites
 
### Generate a service token
To generate a service token:
1. In your dbt Cloud account, go to **Account Settings**.

2. Go to **Service Tokens** and click **+ New Token** to generate a new service token.

3. Copy the token and paste it in a safe place.
 
:::caution
 
Your new token will not be displayed again, so make sure to save it in a safe place.
 
:::
 
## Step 2: Set up the dbt Cloud integration in Airbyte Cloud

To set up the dbt Cloud integration in Airbyte Cloud:
1. On the Airbyte Cloud dashboard, click **Settings** in the navigation bar.

2. In the **Settings** sidebar, click **dbt Cloud integration**.

3. Paste the [service token](https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens) from [Step 1](#step-1-prerequisites) and save the changes.

4. Click **Connections** in the navigation bar and select the connection you want to add a dbt transformation to.

5. Go to the **Transformation** tab and click **+ Add transformation**.

6. Select the transformation from the dropdown and save the changes. The transformation will run during the subsequent syncs until you remove it. 

:::note

You can have multiple transformations per connection.
 
:::

8. To remove a transformation, click **X** on the transformation and save the changes. 
