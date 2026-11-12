# SFTP Bulk

<HideInUI>

This page contains the setup guide and reference information for the [SFTP Bulk](https://docs.airbyte.com/integrations/sources/sftp-bulk#file-specific-configuration) source connector.

</HideInUI>

The SFTP Bulk connector offers several features that are not available in the standard [SFTP](sftp.md) source connector:

- **Bulk ingestion of files**: This connector can consolidate and process multiple files that match a glob pattern as a single stream in your destination.
- **Incremental loading**: This connector supports incremental syncs, so later syncs only read files that were added or modified on the SFTP server since the previous sync. The connector uses each file's last modified time to determine this.
- **Raw file transfer**: In addition to parsing files into records, the connector can copy files as-is to destinations that support file transfers.

## Prerequisites

- Access to a remote server that supports SFTP
- The server's host address and port
- A username and either a password or an SSH private key for that user. Supported private key types are RSA, Ed25519, ECDSA, and DSS.
- Read access to the folder that contains the files you want to sync

## Setup guide

### Step 1: Set up SFTP authentication

Select _one_ of the following authentication methods:

- The username and password associated with the server.
- A private and public key pair.

To set up key pair authentication, follow these steps:

1. Open your terminal or command prompt and use the `ssh-keygen` command to generate a new key pair.

   :::note
   If your operating system doesn't support the `ssh-keygen` command, you can use a third-party tool like [PuTTYgen](https://www.puttygen.com/) to generate the key pair instead.
   :::

2. When prompted, choose a location to save the keys and, optionally, a passphrase. The connector doesn't have a field for a key passphrase, so leave the passphrase empty. The private key is usually saved as `id_rsa` (or `id_ed25519`, depending on the key type), and the public key is saved with the `.pub` extension.

3. Use the `ssh-copy-id` command to copy the public key to the server.

   ```bash
   ssh-copy-id <username>@<server_ip_address>
   ```

   :::note
   Depending on your operating system and the SSH implementation your remote server uses, you may not be able to use the `ssh-copy-id` command. If so, consult your server administrator for the appropriate steps to copy the public key to the server.
   :::

4. Test that you can connect to the server with the private key by using the `ssh` command:

   ```bash
   ssh <username>@<server_ip_address>
   ```

For more information on SSH key pair authentication, see the [SSH key generation documentation](https://www.ssh.com/academy/ssh/keygen).

#### Prepare your private key for Airbyte

If you use key pair authentication, Airbyte needs the full text of your private key.

1. Locate your private key text. This is the block of text that begins with a line like `-----BEGIN OPENSSH PRIVATE KEY-----` or `-----BEGIN RSA PRIVATE KEY-----` and ends with the matching `-----END ... PRIVATE KEY-----` line.

2. Create a PEM file:
   1. Open any text editor.
   2. Create a new file named `ssh.pem`.
   3. Paste the entire private key text into the file, including the BEGIN and END lines.
   4. Make sure there are no quotes or extra spaces before or after the key.
   5. Save the file.

3. (Optional) On macOS or Linux, restrict the file's permissions so only you can read it:

   ```bash
   chmod 600 ssh.pem
   ```

You upload this file to the **Private key** field when you set up the connector in Airbyte.

:::note
The file must be in PEM format: a plain text file containing your private key between the BEGIN and END lines. Don't paste the key directly into the field. Upload the file instead.
:::

### Step 2: Set up the SFTP Bulk connector in Airbyte

1. In Airbyte, click **Sources**, and then click **New source**.
2. Select **SFTP Bulk** from the list of sources.
3. Enter a name for the SFTP Bulk connector.
4. Choose a [delivery method](../../platform/using-airbyte/delivery-methods) for your data.
5. Enter the **Host Address**.
6. Enter your **User Name**.
7. Under **Authentication**, select **Authenticate via Password** or **Authenticate via Private Key**, and then enter your **Password** or upload your **Private key** file. To prepare the file, see [Prepare your private key for Airbyte](#prepare-your-private-key-for-airbyte).
8. Under **The list of streams to sync**, enter a **Stream Name**. This is the name of the stream that Airbyte creates in your destination. Add more streams by clicking **Add**.
9. For each stream, select the **File Type** you want to sync. Depending on the format you choose, you see a set of options specific to that file type. For more information, see [File-specific configuration](#file-specific-configuration).
10. (Optional) Provide a **Start Date** using the date picker, or enter the date in the format `YYYY-MM-DDTHH:mm:ss.SSSSSSZ`. The connector only syncs files modified after this date.
11. (Optional) Specify the **Port**. The default port for SFTP is 22. If your remote server uses a different port, enter it here.
12. (Optional) Enter the **Folder Path**. This is the directory the connector searches for files, and it defaults to `/`. For example, given the following file structure:

    ```text
    Root
    | - logs
    |   | - 2021
    |   | - 2022
    |
    | - files
    |   | - 2021
    |   | - 2022
    ```

    An input of `/logs/2022` replicates only data contained within the specified folder, ignoring the `/files` and `/logs/2021` folders.

13. Click **Set up source**. Airbyte runs a test to verify the configuration.

## Delivery Method

<FieldAnchor field="delivery_method.delivery_type">

Choose a [delivery method](../../platform/using-airbyte/delivery-methods) for your data. **Replicate Records** parses supported file types into records. **Copy Raw Files** transfers files without parsing them, and requires a destination that supports file transfers.

</FieldAnchor>

### Preserve Sub-Directories in File Paths

If enabled, sends subdirectory folder structure along with source file names to the destination. Otherwise, files are synced by their names only. This option is ignored when file-based replication is not enabled.

## File-specific Configuration

Depending on your **File Type** selection, you are presented with a few configuration options specific to that file type.

### Glob patterns

You can specify a **Glob** pattern to select which files should be synced from the file system. Glob patterns work with all supported file types including CSV, Avro, JSONL, Parquet, Excel, and Document formats.

If your files are in a subfolder, include the folder in your glob pattern, like `my_folder/my_prefix_*.csv`. Use `**` to match files recursively in subdirectories, like `**/*.csv`.

## Supported sync modes

The SFTP Bulk source connector supports the following [sync modes](/platform/using-airbyte/core-concepts/sync-modes):

| Feature                        | Support | Notes |
|:-------------------------------|:-------:|:------|
| Full Refresh - Overwrite       |    ✅    |       |
| Full Refresh - Append Sync     |    ✅    |       |
| Incremental - Append           |    ✅    |       |
| Incremental - Append + Deduped |    ❌    |       |

## Supported Streams

This source doesn't have predefined streams. You define each stream in the connector configuration, and each stream syncs all files that match its glob patterns. The connector infers each stream's schema from the files it reads, unless you provide an input schema.

Supported file types are Avro, CSV, JSONL, Parquet, Excel, and Document File Type Format (unstructured documents such as PDF, DOCX, and Markdown).

## File Size Limitations

When using the SFTP Bulk connector with the **Copy Raw Files** delivery method, individual files are subject to a maximum size limit of 1.5 GB (1,500,000,000 bytes) per file. This limitation applies to the raw file transfer process where files are copied without parsing their contents.

If you need to sync files larger than 1.5 GB, consider the following approach:

- Split large files into smaller chunks before uploading them to your SFTP server

The **Replicate Records** delivery method is not a workaround for large file sizes. Replicate Records only works with structured file formats (CSV, JSONL, Parquet, Avro, etc.) that the connector can parse into individual records. It does not support unstructured files or binary formats, and files processed through Replicate Records are still subject to the same size limitations.

For more information about delivery methods and their limitations, see the [Delivery Methods documentation](/platform/using-airbyte/delivery-methods#supported-versions-and-limitations).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                     |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------|
| 1.9.4 | 2026-11-11 | [90893](https://github.com/airbytehq/airbyte/pull/90893) | Require Python 3.11 or later |
| 1.9.3 | 2026-10-22 | [89517](https://github.com/airbytehq/airbyte/pull/89517) | Allow Python 3.13 and upgrade base image to python-connector-base 4.1.1 |
| 1.9.2 | 2026-04-07 | [76108](https://github.com/airbytehq/airbyte/pull/76108) | Catch `struct.error` during private key parsing and re-raise `AirbyteTracedException` instead of swallowing config errors as warnings |
| 1.9.1 | 2026-04-02 | [75967](https://github.com/airbytehq/airbyte/pull/75967) | Support non-RSA private key types (Ed25519, ECDSA, DSS) for SSH authentication |
| 1.9.0 | 2026-01-08 | [71225](https://github.com/airbytehq/airbyte/pull/71225) | Promoting release candidate 1.9.0-rc.2 to a main version. |
| 1.9.0-rc.2 | 2026-01-06 | [71038](https://github.com/airbytehq/airbyte/pull/71038) | Fix directory could match globs logic |
| 1.9.0-rc.1 | 2025-12-22 | [69167](https://github.com/airbytehq/airbyte/pull/69167) | Fix OOM on check, update airbyte-cdk version |
| 1.8.9 | 2025-11-24 | [69833](https://github.com/airbytehq/airbyte/pull/69833) | Increase `maxSecondsBetweenMessages` to 3 hours |
| 1.8.8 | 2025-11-10 | [69257](https://github.com/airbytehq/airbyte/pull/69257) | Update error message when file exceeds size limit |
| 1.8.7 | 2025-10-21 | [68276](https://github.com/airbytehq/airbyte/pull/68276) | Update dependencies |
| 1.8.6 | 2025-10-14 | [67923](https://github.com/airbytehq/airbyte/pull/67923) | Update dependencies |
| 1.8.5 | 2025-10-07 | [67234](https://github.com/airbytehq/airbyte/pull/67234) | Update dependencies |
| 1.8.4 | 2025-09-30 | [66868](https://github.com/airbytehq/airbyte/pull/66868) | Update dependencies |
| 1.8.3 | 2025-09-15 | [66197](https://github.com/airbytehq/airbyte/pull/66197) | Update to CDK v7 |
| 1.8.2 | 2025-08-24 | [60498](https://github.com/airbytehq/airbyte/pull/60498) | Update dependencies |
| 1.8.1 | 2025-05-10 | [58962](https://github.com/airbytehq/airbyte/pull/58962) | Update dependencies |
| 1.8.0 | 2025-05-07 | [57514](https://github.com/airbytehq/airbyte/pull/57514) | Adapt file-transfer records to latest protocol, requires platform >= 1.7.0, destination-s3 >= 1.8.0 |
| 1.7.8 | 2025-04-19 | [58448](https://github.com/airbytehq/airbyte/pull/58448) | Update dependencies |
| 1.7.7 | 2025-04-05 | [57475](https://github.com/airbytehq/airbyte/pull/57475) | Update dependencies |
| 1.7.6 | 2025-03-29 | [56898](https://github.com/airbytehq/airbyte/pull/56898) | Update dependencies |
| 1.7.5 | 2025-03-22 | [54083](https://github.com/airbytehq/airbyte/pull/54083) | Update dependencies |
| 1.7.4 | 2025-02-08 | [53570](https://github.com/airbytehq/airbyte/pull/53570) | Update dependencies |
| 1.7.3 | 2025-02-01 | [52971](https://github.com/airbytehq/airbyte/pull/52971) | Update dependencies |
| 1.7.2 | 2025-01-25 | [52470](https://github.com/airbytehq/airbyte/pull/52470) | Update dependencies |
| 1.7.1 | 2025-01-18 | [43821](https://github.com/airbytehq/airbyte/pull/43821) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.7.0 | 2025-01-17 | [51611](https://github.com/airbytehq/airbyte/pull/51611) | Promoting release candidate 1.7.0-rc.1 to a main version. |
| 1.7.0-rc.1   | 2025-01-16 | [50972](https://github.com/airbytehq/airbyte/pull/50972) | Include option to not mirroring subdirectory structure.     |
| 1.6.0   | 2024-12-17 | [49826](https://github.com/airbytehq/airbyte/pull/49826) | Increase individual file size limit.                        |
| 1.5.0   | 2024-12-02 | [48434](https://github.com/airbytehq/airbyte/pull/48434) | Add get_file method for file-transfer feature.              |
| 1.4.0   | 2024-10-31 | [46739](https://github.com/airbytehq/airbyte/pull/46739) | make private key an airbyte secret.                         |
| 1.3.0   | 2024-10-31 | [47703](https://github.com/airbytehq/airbyte/pull/47703) | Update dependency to CDK v6 with ability to transfer files. |
| 1.2.0   | 2024-09-03 | [46323](https://github.com/airbytehq/airbyte/pull/46323) | Update dependency to CDK v5                                 |
| 1.1.0   | 2024-08-14 | [44028](https://github.com/airbytehq/airbyte/pull/44028) | Update dependency to CDK v4                                 |
| 1.0.1   | 2024-05-29 | [38703](https://github.com/airbytehq/airbyte/pull/38703) | Avoid error on empty stream when running discover           |
| 1.0.0   | 2024-03-22 | [36256](https://github.com/airbytehq/airbyte/pull/36256) | Migrate to File-Based CDK. Manage dependencies with Poetry. |
| 0.1.2   | 2023-04-19 | [19224](https://github.com/airbytehq/airbyte/pull/19224) | Support custom CSV separators                               |
| 0.1.1   | 2023-03-17 | [24180](https://github.com/airbytehq/airbyte/pull/24180) | Fix field order                                             |
| 0.1.0   | 2021-24-05 | [17691](https://github.com/airbytehq/airbyte/pull/17691) | Initial version                                             |

</details>
