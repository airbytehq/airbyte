# FTP
This page contains the setup guide and reference information for the FTP source connector.

## Prerequisites

* The Server with FTP connection type support
* The Server host
* The Server port
* Username-Password/Public Key Access Rights

## Setup guide
### Step 1: Set up FTP
1. Use your username/password credential to connect the server.
2. Alternatively generate Public Key Access

The following simple steps are required to set up public key authentication:

Key pair is created (typically by the user). This is typically done with ssh-keygen.
Private key stays with the user (and only there), while the public key is sent to the server. Typically with the ssh-copy-id utility.
Server stores the public key (and "marks" it as authorized).
Server will now allow access to anyone who can prove they have the corresponding private key.

### Step 2: Set up the FTP connector in Airbyte

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
| 0.1.0   | 2021-24-05 |              | Initial version |
