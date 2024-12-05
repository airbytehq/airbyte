---
products: cloud
---

# Use the dbt Cloud integration

By using the dbt Cloud integration, you can create and run dbt transformations immediately following syncs in Airbyte Cloud. This allows you to transform raw data into a format that is suitable for analysis and reporting, including cleaning and enriching the data.

:::note

Transforming data may cause an increase in your destination's compute cost. This cost will vary depending on the amount of data that is transformed and is not related to Airbyte credit usage.

:::

## Prerequisites
- To use the dbt Cloud integration, you must use a paid version of dbt Cloud.
- The service token must have Member, Job Admin, or Account Admin permissions.

## Step 1: Generate a service token

Generate a [service token](https://docs.getdbt.com/docs/dbt-cloud-apis/service-tokens#generate-service-account-tokens) to enable authentication with dbt Cloud.

## Step 2: Set up the dbt Cloud integration for the workspace

1. Click **Settings** and then **Integrations**. Enter your access URL (for example, `https://cloud.getdbt.com/`). [Custom access URLs](https://docs.getdbt.com/docs/cloud/about-cloud/access-regions-ip-addresses#accessing-your-account) are also supported.

2. Enter the service token and click **Save changes**.

## Step 3: Add a dbt transformation to an individual connection

1. Click **Connections** and select the connection you want to add a dbt transformation to. Go to the **Transformation** tab and click **+ Add transformation**. 

2. Select the dbt job from the dropdown and click **Save changes**. The dbt job will run after the subsequent syncs until you remove it. You can repeat these steps to add additional transformations for a connection.

3. To remove a transformation, click **X** on the transformation and click **Save changes**.
