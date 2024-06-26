# SFTP

This page contains the setup guide and reference information for the SFTP source connector.

## Prerequisites

- Access to a remote server that supports SFTP
- Host address
- Valid username and password associated with the host server

## Setup guide

### Step 1: Set up SFTP authentication

To set up the SFTP connector, you will need to select _one_ of the following authentication methods:

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
   **For Airbyte Cloud users**: If you do not see the **SFTP** source listed, please make sure the **Alpha** checkbox at the top of the page is checked.
   <!-- /env:cloud -->
4. Enter a **Source name** of your choosing.
5. Enter your **Username**, as well as the **Host Address** and **Port**. The default port for SFTP is 22. If your remote server is using a different port, please enter it here.
6. In the **Authentication** section, use the dropdown menu to select **Password Authentication** or **SSH Key Authentication**, then fill in the required credentials. If you are authenticating with a private key, you can upload the file containing the private key (usually named `rsa_id`) using the **Upload file** button.
7. If you wish to configure additional optional settings, please refer to the next section. Otherwise, click **Set up source** and wait for the tests to complete.

## Optional fields

The **Optional fields** can be used to further configure the SFTP source connector. If you do not wish to set additional configurations, these fields can be left at their default settings.

1. **File Types**: Enter the desired file types to replicate as comma-separated values. Currently, only CSV and JSON are supported. The default value is `csv,json`.
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

## Supported sync modes

The SFTP source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                        | Support | Notes                                                                                |
| :----------------------------- | :-----: | :----------------------------------------------------------------------------------- |
| Full Refresh - Overwrite       |   ✅    | Warning: this mode deletes all previously synced data in the configured bucket path. |
| Full Refresh - Append Sync     |   ❌    |                                                                                      |
| Incremental - Append           |   ❌    |                                                                                      |
| Incremental - Append + Deduped |   ❌    |                                                                                      |
| Namespaces                     |   ❌    |                                                                                      |

## Supported streams

This source provides a single stream per file with a dynamic schema. The current supported file types are CSV and JSON.
More formats \(e.g. Apache Avro\) will be supported in the future.

## Changelog
<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                |
| :------ | :--------- | :------------------------------------------------------- | :----------------------------------------------------- |
| 0.2.2   | 2024-02-13 | [35221](https://github.com/airbytehq/airbyte/pull/35221) | Adopt CDK 0.20.4                                       |
| 0.2.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version                                       |
| 0.2.0   | 2024-01-15 | [34265](https://github.com/airbytehq/airbyte/pull/34265) | Remove LEGACY state flag                               |
| 0.1.2   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors |
| 0.1.0   | 2021-24-05 |                                                          | Initial version                                        |

</details>