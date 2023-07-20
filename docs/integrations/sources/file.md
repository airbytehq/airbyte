# Files (CSV, JSON, Excel, Feather, Parquet)

This page contains the setup guide and reference information for the Files source connector.

## Prerequisites

- URL to access the file
- Format
- Reader options
- Storage Providers

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

Setup through Airbyte Cloud will be exactly the same as the open-source setup, except for the fact that local files are disabled.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Once the File Source is selected, you should define both the storage provider along its URL and format of the file.
2. Depending on the provider choice and privacy of the data, you will have to configure more options.
<!-- /env:oss -->

### Fields description

- For `Dataset Name` use the _name_ of the final table to replicate this file into (should include letters, numbers dash and underscores only).
- For `File Format` use the _format_ of the file which should be replicated (Warning: some formats may be experimental, please refer to the docs).
- For `Reader Options` use a _string in JSON_ format. It depends on the chosen file format to provide additional options and tune its behavior. For example, `{}` for empty options, `{"sep": " "}` for set up separator to one space ' '.
- For `URL` use the _URL_ path to access the file which should be replicated.
- For `Storage Provider` use the _storage Provider_ or _Location_ of the file(s) which should be replicated.
  - [Default] _Public Web_
    - `User-Agent` set to active if you want to add User-Agent to requests
  - _GCS: Google Cloud Storage_
    - `Service Account JSON` In order to access private Buckets stored on Google Cloud, this connector would need a service account json credentials with the proper permissions as described <a href="https://cloud.google.com/iam/docs/service-accounts" target="_blank">here</a>. Please generate the credentials.json file and copy/paste its content to this field (expecting JSON formats). If accessing publicly available data, this field is not necessary.
  - _S3: Amazon Web Services_
    - `AWS Access Key ID` In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary.
    - `AWS Secret Access Key`In order to access private Buckets stored on AWS S3, this connector would need credentials with the proper permissions. If accessing publicly available data, this field is not necessary.
  - _AzBlob: Azure Blob Storage_
    - `Storage Account` The globally unique name of the storage account that the desired blob sits within. See <a href="https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview" target="_blank">here</a> for more details.
    - `SAS Token` To access Azure Blob Storage, this connector would need credentials with the proper permissions. One option is a SAS (Shared Access Signature) token. If accessing publicly available data, this field is not necessary.
    - `Shared Key` To access Azure Blob Storage, this connector would need credentials with the proper permissions. One option is a storage account shared key (aka account key or access key). If accessing publicly available data, this field is not necessary.
  - _SSH: Secure Shell_
    - `User` use _username_.
    - `Password` use _password_.
    - `Host` use a _host_.
    - `Port` use a _port_ for your host.
  - _SCP: Secure copy protocol_
    - `User` use _username_.
    - `Password` use _password_.
    - `Host` use a _host_.
    - `Port` use a _port_ for your host.
  - _SFTP: Secure File Transfer Protocol_
    - `User` use _username_.
    - `Password` use _password_.
    - `Host` use a _host_.
    - `Port` use a _port_ for your host.
  - _Local Filesystem (limited)_
    - `Storage` WARNING: Note that the local storage URL available for reading must start with the local mount "/local/" at the moment until we implement more advanced docker mounting options.

#### Provider Specific Information

- In case of Google Drive, it is necesary to use the Download URL, the format for that is `https://drive.google.com/uc?export=download&id=[DRIVE_FILE_ID]` where `[DRIVE_FILE_ID]` is the string found in the Share URL here `https://drive.google.com/file/d/[DRIVE_FILE_ID]/view?usp=sharing`
- In case of GCS, it is necessary to provide the content of the service account keyfile to access private buckets. See settings of [BigQuery Destination](../destinations/bigquery.md)
- In case of AWS S3, the pair of `aws_access_key_id` and `aws_secret_access_key` is necessary to access private S3 buckets.
- In case of AzBlob, we account for the base URL, you should only need to include the path to your file(eg. `container/file.csv`). It is also necessary to provide the `storage_account` in which the blob you want to access resides. Either `sas_token` [(info)](https://docs.microsoft.com/en-us/azure/storage/blobs/sas-service-create?tabs=dotnet) or `shared_key` [(info)](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal) is necessary to access private blobs.
- In case of a locally stored file on a Windows OS, it's necessary to change the values for `LOCAL_ROOT`, `LOCAL_DOCKER_MOUNT` and `HACK_LOCAL_ROOT_PARENT` in the `.env` file to an existing absolute path on your machine (colons in the path need to be replaced with a double forward slash, //). `LOCAL_ROOT` & `LOCAL_DOCKER_MOUNT` should be the same value, and `HACK_LOCAL_ROOT_PARENT` should be the parent directory of the other two.

### Reader Options

The Reader in charge of loading the file format is currently based on [Pandas IO Tools](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html). It is possible to customize how to load the file into a Pandas DataFrame as part of this Source Connector. This is doable in the `reader_options` that should be in JSON format and depends on the chosen file format. See pandas' documentation, depending on the format:

For example, if the format `CSV` is selected, then options from the [read_csv](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-read-csv-table) functions are available.

- It is therefore possible to customize the `delimiter` (or `sep`) to in case of tab separated files.
- Header line can be ignored with `header=0` and customized with `names`
- Parse dates for in specified columns
- etc

We would therefore provide in the `reader_options` the following json:

```
{ "sep" : "\t", "header" : 0, "names": ["column1", "column2"], "parse_dates": ["column2"]}
```

In case you select `JSON` format, then options from the [read_json](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-json-reader) reader are available.

For example, you can use the `{"orient" : "records"}` to change how orientation of data is loaded (if data is `[{column -> value}, … , {column -> value}]`)

If you need to read Excel Binary Workbook, please specify `excel_binary` format in `File Format` select.

    :::warning
    This connector does not support syncing unstructured data files such as raw text, audio, or videos.
    :::

## Supported sync modes

| Feature                                  | Supported? |
| ---------------------------------------- | ---------- |
| Full Refresh Sync                        | Yes        |
| Incremental Sync                         | No         |
| Replicate Incremental Deletes            | No         |
| Replicate Folders (multiple Files)       | No         |
| Replicate Glob Patterns (multiple Files) | No         |

    :::info
    This source produces a single table for the target file as it replicates only one file at a time for the moment. Note that you should provide the `dataset_name` which dictates how the table will be identified in the destination (since `URL` can be made of complex characters).
    :::

## File / Stream Compression

| Compression | Supported? |
| ----------- | ---------- |
| Gzip        | Yes        |
| Zip         | No         |
| Bzip2       | No         |
| Lzma        | No         |
| Xz          | No         |
| Snappy      | No         |

## Storage Providers

| Storage Providers      | Supported?                                      |
| ---------------------- | ----------------------------------------------- |
| HTTPS                  | Yes                                             |
| Google Cloud Storage   | Yes                                             |
| Amazon Web Services S3 | Yes                                             |
| SFTP                   | Yes                                             |
| SSH / SCP              | Yes                                             |
| local filesystem       | Local use only (inaccessible for Airbyte Cloud) |

### File Formats

| Format                | Supported? |
| --------------------- | ---------- |
| CSV                   | Yes        |
| JSON                  | Yes        |
| HTML                  | No         |
| XML                   | No         |
| Excel                 | Yes        |
| Excel Binary Workbook | Yes        |
| Feather               | Yes        |
| Parquet               | Yes        |
| Pickle                | No         |
| YAML                  | Yes        |

### Changing data types of source columns

Normally, Airbyte tries to infer the data type from the source, but you can use `reader_options` to force specific data types. If you input `{"dtype":"string"}`, all columns will be forced to be parsed as strings. If you only want a specific column to be parsed as a string, simply use `{"dtype" : {"column name": "string"}}`.

### Examples

Here are a list of examples of possible file inputs:

| Dataset Name      | Storage | URL                                                                                                                                                        | Reader Impl        | Service Account                                                | Description                                                                                                                                                                                                           |
| ----------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| epidemiology      | HTTPS   | [https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv](https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv) |                    |                                                                | [COVID-19 Public dataset](https://console.cloud.google.com/marketplace/product/bigquery-public-datasets/covid19-public-data-program?filter=solution-type:dataset&id=7d6cc408-53c8-4485-a187-b8cb9a5c0b56) on BigQuery |
| hr_and_financials | GCS     | gs://airbyte-vault/financial.csv                                                                                                                           | smart_open or gcfs | {"type": "service_account", "private_key_id": "XXXXXXXX", ...} | data from a private bucket, a service account is necessary                                                                                                                                                            |
| landsat_index     | GCS     | gcp-public-data-landsat/index.csv.gz                                                                                                                       | smart_open         |                                                                | Using smart_open, we don't need to specify the compression (note the gs:// is optional too, same for other providers)                                                                                                 |

Examples with reader options:

| Dataset Name  | Storage | URL                                             | Reader Impl | Reader Options                | Description                                                                                                                                      |
| ------------- | ------- | ----------------------------------------------- | ----------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| landsat_index | GCS     | gs://gcp-public-data-landsat/index.csv.gz       | GCFS        | {"compression": "gzip"}       | Additional reader options to specify a compression option to `read_csv`                                                                          |
| GDELT         | S3      | s3://gdelt-open-data/events/20190914.export.csv |             | {"sep": "\t", "header": null} | Here is TSV data separated by tabs without header row from [AWS Open Data](https://registry.opendata.aws/gdelt/)                                 |
| server_logs   | local   | /local/logs.log                                 |             | {"sep": ";"}                  | After making sure a local text file exists at `/tmp/airbyte_local/logs.log` with logs file from some server that are delimited by ';' delimiters |

Example for SFTP:

| Dataset Name | Storage | User | Password | Host            | URL                     | Reader Options                                                          | Description                                                                                                                       |
| ------------ | ------- | ---- | -------- | --------------- | ----------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Test Rebext  | SFTP    | demo | password | test.rebext.net | /pub/example/readme.txt | {"sep": "\r\n", "header": null, "names": \["text"], "engine": "python"} | We use `python` engine for `read_csv` in order to handle delimiter of more than 1 character while providing our own column names. |

Please see (or add) more at `airbyte-integrations/connectors/source-file/integration_tests/integration_source_test.py` for further usages examples.

## Performance Considerations and Notes

In order to read large files from a remote location, this connector uses the [smart_open](https://pypi.org/project/smart-open/) library. However, it is possible to switch to either [GCSFS](https://gcsfs.readthedocs.io/en/latest/) or [S3FS](https://s3fs.readthedocs.io/en/latest/) implementations as it is natively supported by the `pandas` library. This choice is made possible through the optional `reader_impl` parameter.

- Note that for local filesystem, the file probably have to be stored somewhere in the `/tmp/airbyte_local` folder with the same limitations as the [CSV Destination](../destinations/csv.md) so the `URL` should also starts with `/local/`.
- Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.
- The JSON implementation needs to be tweaked in order to produce more complex catalog and is still in an experimental state: Simple JSON schemas should work at this point but may not be well handled when there are multiple layers of nesting.

## Changelog

| Version | Date       | Pull Request                                               | Subject                                                                                                 |
|:--------|:-----------|:-----------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
| 0.3.11  | 2023-06-08 | [27157](https://github.com/airbytehq/airbyte/pull/27157)   | Force smart open log level to ERROR                                                                     |
| 0.3.10  | 2023-06-07 | [27107](https://github.com/airbytehq/airbyte/pull/27107)   | Make source-file testable in our new airbyte-ci pipelines                                               |
| 0.3.9   | 2023-05-18 | [26275](https://github.com/airbytehq/airbyte/pull/26275)   | Add ParserError handling                                                                                |
| 0.3.8   | 2023-05-17 | [26210](https://github.com/airbytehq/airbyte/pull/26210)   | Bugfix for https://github.com/airbytehq/airbyte/pull/26115                                              |
| 0.3.7   | 2023-05-16 | [26131](https://github.com/airbytehq/airbyte/pull/26131)   | Re-release source-file to be in sync with source-file-secure                                            |
| 0.3.6   | 2023-05-16 | [26115](https://github.com/airbytehq/airbyte/pull/26115)   | Add retry on SSHException('Error reading SSH protocol banner')                                          |
| 0.3.5   | 2023-05-16 | [26117](https://github.com/airbytehq/airbyte/pull/26117)   | Check if reader options is a valid JSON object                                                          |
| 0.3.4   | 2023-05-10 | [25965](https://github.com/airbytehq/airbyte/pull/25965)   | fix Pandas date-time parsing to airbyte type                                                            |
| 0.3.3   | 2023-05-04 | [25819](https://github.com/airbytehq/airbyte/pull/25819)   | GCP service_account_json is a secret                                                                    |
| 0.3.2   | 2023-05-01 | [25641](https://github.com/airbytehq/airbyte/pull/25641)   | Handle network errors                                                                                   |
| 0.3.1   | 2023-04-27 | [25575](https://github.com/airbytehq/airbyte/pull/25575)   | Fix OOM; read Excel files in chunks using `openpyxl`                                                    |
| 0.3.0   | 2023-04-24 | [25445](https://github.com/airbytehq/airbyte/pull/25445)   | Add datatime format parsing support for csv files                                                       |
| 0.2.38  | 2023-04-12 | [23759](https://github.com/airbytehq/airbyte/pull/23759)   | Fix column data types for numerical values                                                              |
| 0.2.37  | 2023-04-06 | [24525](https://github.com/airbytehq/airbyte/pull/24525)   | Fix examples in spec                                                                                    |
| 0.2.36  | 2023-03-27 | [24588](https://github.com/airbytehq/airbyte/pull/24588)   | Remove traceback from user messages.                                                                    |
| 0.2.35  | 2023-03-03 | [24278](https://github.com/airbytehq/airbyte/pull/24278)   | Read only file header when checking connectivity; read only a single chunk when discovering the schema. |
| 0.2.34  | 2023-03-03 | [23723](https://github.com/airbytehq/airbyte/pull/23723)   | Update description in spec, make user-friendly error messages and docs.                                 |
| 0.2.33  | 2023-01-04 | [21012](https://github.com/airbytehq/airbyte/pull/21012)   | Fix special characters bug                                                                              |
| 0.2.32  | 2022-12-21 | [20740](https://github.com/airbytehq/airbyte/pull/20740)   | Source File: increase SSH timeout to 60s                                                                |
| 0.2.31  | 2022-11-17 | [19567](https://github.com/airbytehq/airbyte/pull/19567)   | Source File: bump 0.2.31                                                                                |
| 0.2.30  | 2022-11-10 | [19222](https://github.com/airbytehq/airbyte/pull/19222)   | Use AirbyteConnectionStatus for "check" command                                                         |
| 0.2.29  | 2022-11-08 | [18587](https://github.com/airbytehq/airbyte/pull/18587)   | Fix pandas read_csv header none issue.                                                                  |
| 0.2.28  | 2022-10-27 | [18428](https://github.com/airbytehq/airbyte/pull/18428)   | Add retry logic for `Connection reset error - 104`                                                      |
| 0.2.27  | 2022-10-26 | [18481](https://github.com/airbytehq/airbyte/pull/18481)   | Fix check for wrong format                                                                              |
| 0.2.26  | 2022-10-18 | [18116](https://github.com/airbytehq/airbyte/pull/18116)   | Transform Dropbox shared link                                                                           |
| 0.2.25  | 2022-10-14 | [17994](https://github.com/airbytehq/airbyte/pull/17994)   | Handle `UnicodeDecodeError` during discover step.                                                       |
| 0.2.24  | 2022-10-03 | [17504](https://github.com/airbytehq/airbyte/pull/17504)   | Validate data for `HTTPS` while `check_connection`                                                      |
| 0.2.23  | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304)   | Migrate to per-stream state.                                                                            |
| 0.2.22  | 2022-09-15 | [16772](https://github.com/airbytehq/airbyte/pull/16772)   | Fix schema generation for JSON files containing arrays                                                  |
| 0.2.21  | 2022-08-26 | [15568](https://github.com/airbytehq/airbyte/pull/15568)   | Specify `pyxlsb` library for Excel Binary Workbook files                                                |
| 0.2.20  | 2022-08-23 | [15870](https://github.com/airbytehq/airbyte/pull/15870)   | Fix CSV schema discovery                                                                                |
| 0.2.19  | 2022-08-19 | [15768](https://github.com/airbytehq/airbyte/pull/15768)   | Convert 'nan' to 'null'                                                                                 |
| 0.2.18  | 2022-08-16 | [15698](https://github.com/airbytehq/airbyte/pull/15698)   | Cache binary stream to file for discover                                                                |
| 0.2.17  | 2022-08-11 | [15501](https://github.com/airbytehq/airbyte/pull/15501)   | Cache binary stream to file                                                                             |
| 0.2.16  | 2022-08-10 | [15293](https://github.com/airbytehq/airbyte/pull/15293)   | Add support for encoding reader option                                                                  |
| 0.2.15  | 2022-08-05 | [15269](https://github.com/airbytehq/airbyte/pull/15269)   | Bump `smart-open` version to 6.0.0                                                                      |
| 0.2.12  | 2022-07-12 | [14535](https://github.com/airbytehq/airbyte/pull/14535)   | Fix invalid schema generation for JSON files                                                            |
| 0.2.11  | 2022-07-12 | [9974](https://github.com/airbytehq/airbyte/pull/14588)    | Add support to YAML format                                                                              |
| 0.2.9   | 2022-02-01 | [9974](https://github.com/airbytehq/airbyte/pull/9974)     | Update airbyte-cdk 0.1.47                                                                               |
| 0.2.8   | 2021-12-06 | [8524](https://github.com/airbytehq/airbyte/pull/8524)     | Update connector fields title/description                                                               |
| 0.2.7   | 2021-10-28 | [7387](https://github.com/airbytehq/airbyte/pull/7387)     | Migrate source to CDK structure, add SAT testing.                                                       |
| 0.2.6   | 2021-08-26 | [5613](https://github.com/airbytehq/airbyte/pull/5613)     | Add support to xlsb format                                                                              |
| 0.2.5   | 2021-07-26 | [4953](https://github.com/airbytehq/airbyte/pull/4953)     | Allow non-default port for SFTP type                                                                    |
| 0.2.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)     | Add AIRBYTE_ENTRYPOINT for Kubernetes support                                                           |
| 0.2.3   | 2021-06-01 | [3771](https://github.com/airbytehq/airbyte/pull/3771)     | Add Azure Storage Blob Files option                                                                     |
| 0.2.2   | 2021-04-16 | [2883](https://github.com/airbytehq/airbyte/pull/2883)     | Fix CSV discovery memory consumption                                                                    |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)     | Fix base connector versioning                                                                           |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)     | Protocol allows future/unknown properties                                                               |
| 0.1.10  | 2021-02-18 | [2118](https://github.com/airbytehq/airbyte/pull/2118)     | Support JSONL format                                                                                    |
| 0.1.9   | 2021-02-02 | [1768](https://github.com/airbytehq/airbyte/pull/1768)     | Add test cases for all formats                                                                          |
| 0.1.8   | 2021-01-27 | [1738](https://github.com/airbytehq/airbyte/pull/1738)     | Adopt connector best practices                                                                          |
| 0.1.7   | 2020-12-16 | [1331](https://github.com/airbytehq/airbyte/pull/1331)     | Refactor Python base connector                                                                          |
| 0.1.6   | 2020-12-08 | [1249](https://github.com/airbytehq/airbyte/pull/1249)     | Handle NaN values                                                                                       |
| 0.1.5   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)     | Add connectors using an index YAML file                                                                 |
