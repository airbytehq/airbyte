# SFTP  Bulk
This page contains the setup guide and reference information for the FTP source connector.

This connector allows you to:
- Fetch files from an FTP server matching a folder path and define an optional file pattern to bulk ingest files into a single stream
- Incrementally load files into your destination from an FTP server based on when files were last added or modified
- Optionally load only the latest file matching a folder path and optional pattern and overwrite the data in your destination (helpful when a snapshot file gets added on a regular basis containing the latest data)

## Prerequisites

* The Server with FTP connection type support
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

1. In the left navigation bar, click **`Sources`**. In the top-right corner, click **+new source**.
2. On the Set up the source page, enter the name for the FTP connector and select **SFTP Bulk** from the Source type dropdown.
3. Enter your `User Name`, `Host Address`, `Port`
4. Enter authentication details for the FTP server (`Password` and/or `Private Key`)
5. Choose a `File type`
6. Enter `Folder Path` (Optional) to specify server folder for sync
7. Enter `File Pattern` (Optional). e.g. ` log-([0-9]{4})([0-9]{2})([0-9]{2})`. Write your own [regex](https://docs.python.org/3/howto/regex.html)
8. Check `Most recent file` (Optional) if you only want to sync the most recent file matching a folder path and optional file pattern
9. Provide a `Start Date` for incremental syncs to only sync files modified/added after this date
10. Click on `Check Connection` to finish configuring the FTP source.

## Supported sync modes

The FTP source connector supports the following[ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Support  | Notes                                                                                 |
|:------------------------------|:--------:|:--------------------------------------------------------------------------------------|
| Full Refresh - Overwrite      |    ✅    |                                                                                      |
| Full Refresh - Append Sync    |    ✅    |                                                                                      |
| Incremental - Append          |    ✅    |                                                                                      |
| Incremental - Deduped History |    ❌    |                                                                                      |
| Namespaces                    |    ❌    |                                                                                      |


## Supported Streams

This source provides a single stream per file with a dynamic schema. The current supported type file: `.csv` and `.json`
More formats \(e.g. Apache Avro\) will be supported in the future.

## Changelog

| Version | Date       | Pull Request | Subject         |
|:--------|:-----------|:-------------|:----------------|
| 0.1.2   | 2023-04-19 | [#19224](https://github.com/airbytehq/airbyte/pull/19224) | Support custom CSV separators |
| 0.1.1   | 2023-03-17 | [#24180](https://github.com/airbytehq/airbyte/pull/24180) | Fix field order |
| 0.1.0   | 2021-24-05 |              | Initial version |
