# Using the dbt Cloud integration 

## Step 1: Generate a service token

Generate a [service token](https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens#generating-service-account-tokens) for your dbt Cloud transformation.  

:::note

* To use the dbt Cloud integration, you must use a paid version of dbt Cloud.
* The service token must have Member, Job Admin, or Account Admin permissions.
 
:::

## Step 2: Set up the dbt Cloud integration in Airbyte Cloud

To set up the dbt Cloud integration in Airbyte Cloud:

1. On the Airbyte Cloud dashboard, click **Settings**.

2. Click **dbt Cloud integration**.

3. Paste the service token from [Step 1](#step-1-prerequisites) and click **Save changes**.

4. Click **Connections** and select the connection you want to add a dbt transformation to.

5. Go to the **Transformation** tab and click **+ Add transformation**.

6. Select the transformation from the dropdown and click **Save changes**. The transformation will run during the subsequent syncs until you remove it. 

:::note

You can have multiple transformations per connection.
 
:::

8. To remove a transformation, click **X** on the transformation and click **Save changes**. 
