# SFTP Bulk

This page contains the setup guide and reference information for the SFTP Bulk source connector.

This connector provides the following features not found in the standard SFTP source connector:

- **Bulk ingestion of files**: This connector can consolidate and process multiple files as a single data stream in your destination system.
- **Incremental loading**: This connector supports incremental loading, allowing you to sync files from the SFTP server to your destination based on their creation or last modification time.
- **Load most recent file**: You can choose to load only the most recent file from the designated folder path. This feature is particularly useful when dealing with snapshot files that are regularly added and contain the latest data.

## Prerequisites

- Access to a remote server that supports SFTP
- Host address
- Valid username and password associated with the host server

## Setup guide

### Step 1: Set up SFTP authentication

To set up the SFTP connector, you will need to select at least _one_ of the following authentication methods:

- Your username and password credentials associated with the server.
- A private/public key pair.

To set up key pair authentication, you may use the following steps as a guide:

1. Open your terminal or command prompt and use the `ssh-keygen` command to generate a new key pair.
   :::note
   If your operating system does not support the `ssh-keygen` command, you can use a third-party tool like [PuTTYgen](https://www.puttygen.com/) to generate the key pair instead.
   :::

2. You will be prompted for a location to save the keys, and a passphrase to secure the private key. You can press enter to accept the default location and opt out of a passphrase if desired. Your two keys will be generated in the designated location as two separate files. The private key will usually be saved as `id_rsa`, while the public key will be saved with the `.pub` extension (`id_rsa.pub`).

3. Use the `ssh-copy-id` command in your terminal to copy the public key to the server.

```
ssh-copy-id <username>@<server_ip_address>
```

Be sure to replace your specific values for your username and the server's IP address.
:::note
Depending on factors such as your operating system and the specific SSH implementation your remote server uses, you may not be able to use the `ssh-copy-id` command. If so, please consult your server administrator for the appropriate steps to copy the public key to the server.
:::

4. You should now be able to connect to the server via the private key. You can test this by using the `ssh` command:

```
ssh <username>@<server_ip_address>
```

For more information on SSH key pair authentication, please refer to the
[official documentation](https://www.ssh.com/academy/ssh/keygen).

### Step 2: Set up the SFTP connector in Airbyte

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account, or navigate to your Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **SFTP** from the list of available sources.
   <!-- env:cloud -->
   **For Airbyte Cloud users**: If you do not see the **SFTP Bulk** source listed, please make sure the **Alpha** checkbox at the top of the page is checked.
   <!-- /env:cloud -->
4. Enter a **Source name** of your choosing.
5. Enter your **Username**, as well as the **Host Address** and **Port**. The default port for SFTP is 22. If your remote server is using a different port, please enter it here.
6. Enter your authentication credentials for the SFTP server (**Password** or **Private Key**). If you are authenticating with a private key, you can upload the file containing the private key (usually named `rsa_id`) using the Upload file button.
7. Enter a **Stream Name**. This will be the name of the stream that will be outputted to your destination.
8. Use the dropdown menu to select the **File Type** you wish to sync. Currently, only CSV and JSON formats are supported.
9. Provide a **Start Date** using the provided datepicker, or by programmatically entering the date in the format `YYYY-MM-DDT00:00:00Z`. Incremental syncs will only sync files modified/added after this date.
10. If you wish to configure additional optional settings, please refer to the next section. Otherwise, click **Set up source** and wait for the tests to complete.

## Optional fields

The **Optional fields** can be used to further configure the SFTP source connector. If you do not wish to set additional configurations, these fields can be left at their default settings.

1. **CSV Separator**: If you selected `csv` as the file type, you can use this field to specify a custom separator. The default value is `,`.

2. **Folder Path**: Enter a folder path to specify the directory on the remote server to be synced. For example, given the file structure:

```
Root
| - logs
|   | - 2021
|   | - 2022
|
| - files
|   | - 2021
|   | - 2022
```

An input of `/logs/2022` will only replicate data contained within the specified folder, ignoring the `/files` and `/logs/2021` folders. Leaving this field blank will replicate all applicable files in the remote server's designated entry point.

3. **File Pattern**: Enter a [regular expression](https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html) to specify a naming pattern for the files to be replicated. Consider the following example:

```
log-([0-9]{4})([0-9]{2})([0-9]{2})
```

This pattern will filter for files that match the format `log-YYYYMMDD`, where `YYYY`, `MM`, and `DD` represented four-digit, two-digit, and two-digit numbers, respectively. For example, `log-20230713`. Leaving this field blank will replicate all files not filtered by the previous two fields.

4. **Most Recent File**: Toggle this option if you only want to sync the most recent file located in the folder path. This may be useful when dealing with data sources that generate frequent updates, such as log files or real-time data feeds. Set to False by default.

## Supported sync modes

The SFTP Bulk source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                        | Support | Notes |
| :----------------------------- | :-----: | :---- |
| Full Refresh - Overwrite       |   ✅    |       |
| Full Refresh - Append Sync     |   ✅    |       |
| Incremental - Append           |   ✅    |       |
| Incremental - Append + Deduped |   ❌    |       |
| Namespaces                     |   ❌    |       |

## Supported streams

This source provides a single stream per file with a dynamic schema. The current supported type files are CSV and JSON.
More formats \(e.g. Apache Avro\) will be supported in the future.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                     |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------- |
| 1.0.0   | 2024-03-22 | [36256](https://github.com/airbytehq/airbyte/pull/36256) | Migrate to File-Based CDK. Manage dependencies with Poetry. |
| 0.1.2   | 2023-04-19 | [19224](https://github.com/airbytehq/airbyte/pull/19224) | Support custom CSV separators                               |
| 0.1.1   | 2023-03-17 | [24180](https://github.com/airbytehq/airbyte/pull/24180) | Fix field order                                             |
| 0.1.0   | 2021-24-05 |                                                          | Initial version                                             |
