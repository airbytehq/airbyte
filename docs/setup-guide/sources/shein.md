# Shein

This page contains the setup guide and reference information for Shein.

## Prerequisites

* Shein access account
* openKeyId
* secretKey

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Obtain Shein setup details

1. Apply for Shein [Access account](https://openapi-portal.sheincorp.com/#/home)

2. Obtain **openKeyId** and **secretKey** which you will need to set up Shein in Daspire.

3. You're ready to set up Shein in Daspire!

### Step 2: Set up Shein in Daspire

1. Select **Shein** from the Source list.

2. Enter a **Source Name**.

3. Enter your Shein **openKeyId**.

4. Enter your Shein **secretKey**.

5. In **Data Replication Schedule**, choose an option between **Based on Start Date** or **Periodic Replication**.

6. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Order](https://openapi-portal.sheincorp.com/#/home/2/1)

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.