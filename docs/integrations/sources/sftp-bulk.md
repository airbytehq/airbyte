# SFTP Bulk

<HideInUI>

This page contains the setup guide and reference information for the [SFTP Bulk](https://docs.airbyte.com/integrations/sources/sftp-bulk) source connector.

</HideInUI>

The SFTP Bulk connector offers several features that are not available in the standard SFTP source connector:

- **Bulk ingestion of files**: Consolidate and process multiple files as a single data stream in your destination.
- **Incremental loading**: Sync files from the SFTP server to your destination based on their last modification time.
- **Load most recent file**: Load only the most recent file from a folder path. This is useful for snapshot files that are regularly added and contain the latest data.

## Prerequisites

- Access to a remote server that supports SFTP
- Host address and port (default: 22)
- Username and one of the following authentication credentials:
  - Password
  - SSH private key (RSA, Ed25519, ECDSA, or DSS)

## Setup guide

### Step 1: Set up SFTP authentication

To set up the SFTP Bulk connector, choose one of the following authentication methods:

- **Password**: Use your username and password credentials for the SFTP server.
- **Private key**: Use an SSH key pair. The connector supports RSA, Ed25519, ECDSA, and DSS key types.

To set up key pair authentication:

1. Open a terminal and use `ssh-keygen` to generate a new key pair:

   ```bash
   ssh-keygen -t ed25519
   ```

   You can replace `ed25519` with `rsa`, `ecdsa`, or `dsa` depending on your requirements.

   :::note
   If your operating system does not support `ssh-keygen`, use a third-party tool like [PuTTYgen](https://www.puttygen.com/) to generate the key pair.
   :::

2. When prompted, choose a location to save the keys and optionally set a passphrase. The private key is saved as `id_ed25519` (or `id_rsa`, etc.) and the public key with a `.pub` extension.

3. Copy the public key to the server:

   ```bash
   ssh-copy-id <username>@<server_ip_address>
   ```

   :::note
   If `ssh-copy-id` is not available on your system, consult your server administrator for the appropriate steps to install the public key on the server.
   :::

4. Test the connection:

   ```bash
   ssh <username>@<server_ip_address>
   ```

For more information, refer to the [SSH key pair documentation](https://www.ssh.com/academy/ssh/keygen).

### Step 2: Set up the SFTP Bulk connector in Airbyte

<!-- env:cloud -->

<HideInUI>

#### For Airbyte Cloud:

</HideInUI>

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **SFTP Bulk** from the Source type dropdown.
4. Enter a name for the SFTP Bulk connector.
5. Choose a [delivery method](../../platform/using-airbyte/delivery-methods) for your data.
6. Enter the **Host Address**.
7. Enter your **Username**.
8. Enter your authentication credentials for the SFTP server (**Password** or **Private Key**). If using Private Key authentication, see the [Private key setup](#private-key-setup) section for detailed instructions.
9. In the section titled **The list of streams to sync**, enter a **Stream Name**. Add additional streams by clicking **Add**.
10. For each stream, select the **File Type** you want to sync. Depending on the format chosen, additional format-specific options appear.
11. (Optional) Provide a **Start Date** using the provided datepicker, or by entering the date in the format `YYYY-MM-DDTHH:mm:ss.SSSSSSZ`. Incremental syncs only sync files modified or added after this date.
12. (Optional) Specify the **Port**. The default port for SFTP is 22.
13. (Optional) Set the **Folder Path** to limit syncing to a specific directory. Defaults to `/`. For example, given the file structure:

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

    An input of `/logs/2022` syncs only files within that folder.

14. Click **Set up source** to complete setup. A connection test runs to verify the configuration.

<!-- /env:cloud -->

<!-- env:oss -->

<HideInUI>

#### For Airbyte Open Source:

</HideInUI>

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **SFTP Bulk** from the Source type dropdown.
4. Enter a name for the SFTP Bulk connector.
5. Follow the same configuration steps as described in the Cloud setup, starting from step 5.

<!-- /env:oss -->

#### Private key setup

If your SFTP server uses SSH key-based authentication, provide your private key during setup. The connector supports RSA, Ed25519, ECDSA, and DSS key types.

1. **Locate your private key text.** This is the block of text that begins with a line like `-----BEGIN OPENSSH PRIVATE KEY-----` and ends with `-----END OPENSSH PRIVATE KEY-----`. For older RSA keys, the header may read `-----BEGIN RSA PRIVATE KEY-----`.

2. **Create a PEM file:**
   1. Open a text editor.
   2. Create a new file named `ssh.pem`.
   3. Paste the entire private key text into the file, including the BEGIN and END lines.
   4. Make sure there are no extra quotes or whitespace before or after the key.
   5. Save the file.

3. **(Optional)** On macOS or Linux, restrict file permissions:

   ```bash
   chmod 600 ssh.pem
   ```

4. **Upload the file in Airbyte:**
   1. In the SFTP Bulk source setup form, find the **Private key** field.
   2. Click **Upload file** and select your saved `ssh.pem` file.

:::note
The file must be in PEM format — a plain text file containing your private key between the BEGIN and END lines.
:::

## Delivery method

<FieldAnchor field="delivery_method.delivery_type">

Choose a [delivery method](../../platform/using-airbyte/delivery-methods) for your data.

</FieldAnchor>

### Preserve sub-directories in file paths

If enabled, sends subdirectory folder structure along with source file names to the destination. Otherwise, files are synced by their names only. This option is ignored when file-based replication is not enabled.

## File-specific configuration

Depending on your **File Type** selection, you are presented with configuration options specific to that file type.

### Glob patterns

You can specify a **Glob** pattern to select which files to sync from the file system. Glob patterns work with all supported file types including CSV, Avro, JSONL, Parquet, Excel, and Document formats.

If your files are in a subfolder, include the folder in your glob pattern, like `my_folder/my_prefix_*.csv`. Use `**` to match files recursively in subdirectories, like `**/*.csv`.

## Supported sync modes

The SFTP Bulk source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature                        | Support | Notes |
|:-------------------------------|:-------:|:------|
| Full Refresh - Overwrite       |    ✅    |       |
| Full Refresh - Append Sync     |    ✅    |       |
| Incremental - Append           |    ✅    |       |
| Incremental - Append + Deduped |    ❌    |       |

## Supported streams

This source provides a single stream per file with a dynamic schema. Supported file types are Avro, CSV, JSONL, Parquet, Excel, and Document.

## File size limitations

When using the SFTP Bulk connector with the **Copy Raw Files** delivery method, individual files are subject to a maximum size limit of 1.5 GB per file. This limitation applies to the raw file transfer process where files are copied without parsing their contents.

If you need to sync files larger than 1.5 GB, split them into smaller chunks before uploading them to your SFTP server.

The **Replicate Records** delivery method is not a workaround for large file sizes. Replicate Records only works with structured file formats (CSV, JSONL, Parquet, Avro) that the connector can parse into individual records. It does not support unstructured files or binary formats, and files processed through Replicate Records are still subject to the same size limitations.

For more information about delivery methods and their limitations, see the [Delivery Methods documentation](/platform/using-airbyte/delivery-methods#supported-versions-and-limitations).

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                     |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------|
| 1.9.2 | 2026-04-07 | [76108](https://github.com/airbytehq/airbyte/pull/76108) | Catch `struct.error` during private key parsing and re-raise `AirbyteTracedException` instead of swallowing config errors as warnings |
| 1.9.1 | 2026-04-02 | [75967](https://github.com/airbytehq/airbyte/pull/75967) | Support non-RSA private key types (Ed25519, ECDSA, DSS) for SSH authentication |
| 1.9.0 | 2026-01-08 | [71225](https://github.com/airbytehq/airbyte/pull/71225) | Promoting release candidate 1.9.0-rc.2 to a main version. |
| 1.9.0-rc.2 | 2026-01-06 | [71038](https://github.com/airbytehq/airbyte/pull/71038) | Fix directory could match globs logic |
| 1.9.0-rc.1 | 2025-12-22 | [69167](https://github.com/airbytehq/airbyte/pull/69167) | Fix OOM on check, update airbyte-cdk version |
| 1.8.9 | 2025-11-24 | [69833](https://github.com/airbytehq/airbyte/pull/69833) | Increase `maxSecondsBetweenMessages` to 3 hours |
| 1.8.8 | 2025-11-10 | [69257](https://github.com/airbytehq/airbyte/pull/69257) | Update error message when file exceeds size limit |
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
