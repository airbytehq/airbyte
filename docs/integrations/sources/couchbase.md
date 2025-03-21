# Couchbase

This page contains the setup guide and reference information for the Couchbase source connector.

## Prerequisites

- A Couchbase server version 7.0 or above, or a Couchbase Capella account
- Couchbase connection string
- Couchbase username and password

## Setup guide

### Step 1: Set up Couchbase

#### Option A: Couchbase Capella (Cloud)

1. Create a Couchbase Capella account:
   - Go to the [Couchbase Capella signup page](https://cloud.couchbase.com/sign-up).
   - Follow the prompts to create your account.

2. Create a Capella cluster:
   - Log in to your Capella account.
   - Click on "Create Cluster" in the dashboard.
   - Choose your cloud provider (AWS, Azure, or GCP) and the region where you want to deploy your cluster.
   - Select the cluster size and configuration that suits your needs.
   - Click "Create Cluster" and wait for the deployment to complete (this may take a few minutes).

3. Set up database access:
   - In the Capella UI, navigate to "Security" > "Database Access".
   - Click "Add User" to create a new database user.
   - Provide a username and password for the new user.
   - Assign appropriate roles to the user (e.g., "Data Reader" and "Data Writer" for the buckets you want to replicate).
   - Click "Save" to create the user.

4. Configure allowed IP ranges:
   - In the Capella UI, go to "Security" > "Allowed IP Addresses".
   - Click "Add Allowed IP".
   - Enter the IP address or CIDR range from which your Airbyte instance will connect.
   - Add a description for the IP range (e.g., "Airbyte Connection").
   - Click "Add" to save the allowed IP range.

5. Obtain cluster credentials:
   - In the Capella UI, go to the "Connect" tab for your cluster.
   - You will find the connection string, which typically looks like: `couchbases://cb.<your-cluster-id>.cloud.couchbase.com`
   - Note down this connection string, as you'll need it to configure the Airbyte connector.

#### Option B: Self-hosted Couchbase

1. Ensure your Couchbase server (version 7.0 or above) is up and running.
2. Create a user with appropriate permissions to access the data you want to replicate.

### Step 2: Set up the Couchbase connector in Airbyte

1. In the Airbyte UI, navigate to the Sources page and select Couchbase from the list of available sources.
2. Enter a name for your source.
3. Enter the Couchbase connection string:
   - For Capella: Use the connection string you obtained from the "Connect" tab (e.g., `couchbases://cb.<your-cluster-id>.cloud.couchbase.com`).
   - For self-hosted: Use your server's connection string (e.g., `couchbase://localhost`).
4. Enter the username and password for your Couchbase account (use the credentials you created in Step 1.3 for Capella).
5. Enter the name of the bucket you want to replicate.
6. (Optional) Enter a JSON object of additional properties to be passed to the Couchbase client.

## Supported sync modes

The Couchbase source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
|:------------------------------|:-----------|
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | Yes        |
| Replicate Incremental Deletes | No         |
| CDC                           | No         |

## Supported Streams

The Couchbase source connector will replicate all collections within the specified bucket as individual streams.

## Performance considerations

The connector is rate limited by the Couchbase server or Couchbase Capella cluster's capacity. You may need to adjust the batch size and number of workers based on your server's capacity and network conditions.

For Capella users, be aware of your cluster's performance limits and pricing tier. You may need to upgrade your cluster if you're replicating large amounts of data or require higher throughput.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------|
| 0.1.1 | 2025-03-08 | [55324](https://github.com/airbytehq/airbyte/pull/55324) | Update dependencies |
| 0.1.0   | 2023-10-12 | [#45876](https://github.com/airbytehq/airbyte/pull/45876) | Initial release of Couchbase Source Connector |
