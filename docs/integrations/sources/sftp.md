# SFTP
This page contains the setup guide and reference information for the SFTP source connector.

## Prerequisites

* The Server with SFTP connection type support
* The Server host
* The Server port
* Username-Password/Public Key Access Rights

## Setup guide
### Step 1: Set up SFTP 
1. Use your username/password credential to connect the server.
2. Alternatively generate Public Key Access

The following simple steps are required to set up public key authentication:

Key pair is created (typically by the user). This is typically done with ssh-keygen.
Private key stays with the user (and only there), while the public key is sent to the server. Typically with the ssh-copy-id utility.
Server stores the public key (and "marks" it as authorized).
Server will now allow access to anyone who can prove they have the corresponding private key.

### Step 2: Set up the SFTP connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **`Sources`**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the SFTP connector and select **SFTP** from the Source type dropdown.
4. Enter your `User Name`, `Host Address`, `Port`
5. Choose the `Authentication` type `Password Authentication` or `Key Authentication`
6. Type `File type` (temporary comma separated)
7. Enter `Folder Path` (Optional) to specify server folder for sync
8. Enter `File Pattern` (Optional). e.g. ` log-([0-9]{4})([0-9]{2})([0-9]{2})`. Write your own [regex](https://www.tutorialspoint.com/java/java_regular_expressions.htm)    
9. Click on `Check Connection` to finish configuring the Amplitude source.

## Supported sync modes

The SFTP source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Support | Notes                                                                                |
|:------------------------------|:-------:|:-------------------------------------------------------------------------------------|
| Full Refresh - Overwrite      |    ✅    | Warning: this mode deletes all previously synced data in the configured bucket path. |
| Full Refresh - Append Sync    |    ❌    |                                                                                      |
| Incremental - Append          |    ❌    |                                                                                      |
| Incremental - Deduped History |    ❌    |                                                                                      |
| Namespaces                    |    ❌    |                                                                                      |




## Supported Streams

This source provides a single stream per file with a dynamic schema. The current supported type file: `.csv` and `.json`
More formats \(e.g. Apache Avro\) will be supported in the future.

## Changelog

| Version | Date       | Pull Request | Subject         |
|:--------|:-----------|:-------------|:----------------|
| 0.1.2 | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.0   | 2021-24-05 |              | Initial version |
