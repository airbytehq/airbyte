# SFTP JSON

## Overview

This destination writes data to a directory on an SFTP server. It supports multiple file formats, custom file naming patterns, and flexible directory organization.

### Sync Overview

#### Output schema

Each stream will be output into its own file according to the configured file format and naming pattern.

For JSON format (default), each file will contain a collection of JSON objects which correspond directly with the data supplied by the source.

For CSV format, each file will contain a header row followed by data rows, with field names derived from the source data.

#### Features

| Feature                       | Supported |
| :---------------------------- | :-------- |
| Full Refresh Sync             | Yes       |
| Incremental - Append Sync     | Yes       |
| Namespaces                    | No        |
| Multiple file formats         | Yes       |
| Custom file naming            | Yes       |
| Directory organization        | Yes       |
| Custom SSH algorithms         | Yes       |

#### Performance considerations

This integration will be constrained by the connection speed to the SFTP server and speed at which that server accepts writes.

## Getting Started

### Basic Configuration

- **Host**: The hostname of your SFTP server
- **Port**: The port to connect to (default: 22)
- **Username**: The username to authenticate with
- **Password**: The password to authenticate with
- **Destination Path**: The base directory path where files will be written

### File Format Options

- **File Format**: Choose between `json` (default) or `csv` format
  - JSON files will have the `.jsonl` extension
  - CSV files will have the `.csv` extension

### File Naming Patterns

The `file_name_pattern` parameter allows customizing how files are named. If not specified, the default pattern `airbyte_{format}_{stream}` is used.

Available variables for the naming pattern:
- `{format}`: The file format (json or csv)
- `{stream}`: The name of the data stream
- `{date}`: The current date in YYYYMMDD format

### Directory Organization

You can include directory separators (`/`) in your file naming pattern to organize files into subdirectories:

- `{stream}/{format}` - Organizes by stream name first
- `{format}/{stream}` - Organizes by format first
- `data/{date}/{stream}` - Organizes by date and then stream

All directories will be created automatically if they don't exist.

### SSH Algorithm Configuration

For servers with specific SSH algorithm requirements, you can configure custom SSH algorithms:

```json
{
  "ssh_algorithms": {
    "server_host_key": ["ssh-rsa", "ecdsa-sha2-nistp256"],
    "key_exchange": ["diffie-hellman-group-exchange-sha256"],
    "cipher": ["aes256-ctr", "aes192-ctr"],
    "mac": ["hmac-sha2-512", "hmac-sha2-256"]
  }
}
```

## Examples

### JSON Format with Default Naming

If `destination_path` is set to `/myfolder/files`, file format is `json`, and the default naming pattern is used:
- Stream "customers" → `/myfolder/files/airbyte_json_customers.jsonl`
- Stream "orders" → `/myfolder/files/airbyte_json_orders.jsonl`

### CSV Format with Custom Naming

If `destination_path` is set to `/data`, file format is `csv`, and `file_name_pattern` is set to `{stream}_data`:
- Stream "customers" → `/data/customers_data.csv`
- Stream "orders" → `/data/orders_data.csv`

### Directory Organization

If `destination_path` is set to `/exports`, file format is `json`, and `file_name_pattern` is set to `{format}/{date}/{stream}`:
- Stream "customers" → `/exports/json/20250507/customers.jsonl`
- Stream "orders" → `/exports/json/20250507/orders.jsonl`

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                           | Subject                       |
| :------ | :--------- | :----------------------------------------------------- | :---------------------------- |
| 0.3.0   | 2025-05-07 | [NEW PR NUMBER]                                        | Add support for file formats, custom naming patterns, directory organization, and SSH algorithms |
| 0.2.13  | 2025-05-03 | [59353](https://github.com/airbytehq/airbyte/pull/59353) | Update dependencies |
| 0.2.12  | 2025-04-26 | [58727](https://github.com/airbytehq/airbyte/pull/58727) | Update dependencies |
| 0.2.11  | 2025-04-19 | [58238](https://github.com/airbytehq/airbyte/pull/58238) | Update dependencies |
| 0.2.10  | 2025-04-12 | [57592](https://github.com/airbytehq/airbyte/pull/57592) | Update dependencies |
| 0.2.9   | 2025-04-05 | [57114](https://github.com/airbytehq/airbyte/pull/57114) | Update dependencies |
| 0.2.8   | 2025-03-29 | [56615](https://github.com/airbytehq/airbyte/pull/56615) | Update dependencies |
| 0.2.7   | 2025-03-22 | [56090](https://github.com/airbytehq/airbyte/pull/56090) | Update dependencies |
| 0.2.6   | 2025-03-08 | [55369](https://github.com/airbytehq/airbyte/pull/55369) | Update dependencies |
| 0.2.5   | 2025-03-01 | [54868](https://github.com/airbytehq/airbyte/pull/54868) | Update dependencies |
| 0.2.4   | 2025-02-22 | [54265](https://github.com/airbytehq/airbyte/pull/54265) | Update dependencies |
| 0.2.3   | 2025-02-15 | [53941](https://github.com/airbytehq/airbyte/pull/53941) | Update dependencies |
| 0.2.2   | 2025-02-08 | [53405](https://github.com/airbytehq/airbyte/pull/53405) | Update dependencies |
| 0.2.1   | 2025-02-01 | [52883](https://github.com/airbytehq/airbyte/pull/52883) | Update dependencies |
| 0.2.0   | 2024-10-14 | [46873](https://github.com/airbytehq/airbyte/pull/46873) | Migrated to Poetry and Airbyte Base Image |
| 0.1.0   | 2022-11-24 | [4924](https://github.com/airbytehq/airbyte/pull/4924) | 🎉 New Destination: SFTP JSON |
</details>