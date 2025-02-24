# Google Cloud Storage (GCS)

<HideInUI>

This page contains the setup guide and reference information for the [Google Cloud Storage (GCS)](https://cloud.google.com/storage/docs/apis) source connector.

</HideInUI>

:::info
Cloud storage may incur egress costs. Egress refers to data that is transferred out of the cloud storage system, such as when you download files or access them from a different location. For more information, see the [Google Cloud Storage pricing guide](https://cloud.google.com/storage/pricing).
:::

## Prerequisites

- Google account or JSON credentials for the service account that have access to GCS. For more details check [instructions](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
- GCS bucket
- The list of streams to sync

## Setup guide

## Set up Google Cloud Storage (GCS)

### Create a Service Account

First, you need to select existing or create a new project in the Google Cloud Console:

1. Sign in to the Google Account.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page.
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `service_account` in the UI.

### Grant permission to GCS

Use the service account ID from above, grant read access to your target bucket. Click [here](https://cloud.google.com/storage/docs/access-control/using-iam-permissions) for more details.

### Set up the Google Cloud Storage (GCS) connector in Airbyte

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Google Cloud Storage (GCS) from the Source type dropdown.
4. Enter a name for the Google Cloud Storage (GCS) connector.
5. Select authorization type:
   1. **Authenticate via Google (OAuth)** from the Authentication dropdown, click **Sign in with Google** and complete the authentication workflow. 
   2. **Service Account Information** and paste the service account JSON key to the `Service Account Information` field .
6. Paste the service account JSON key to the `Service Account Information` field .
7. Enter your GCS bucket name to the `Bucket` field. 
8. Add a stream:
   1. Give a **Name** to the stream 
   2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below. 
   3. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
   4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
9. Configure the optional **Start Date** parameter that marks a starting date and time in UTC for data replication. Any files that have _not_ been modified since this specified date/time will _not_ be replicated. Use the provided datepicker (recommended) or enter the desired date programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. Leaving this field blank will replicate data from all files that have not been excluded by the **Path Pattern** and **Path Prefix**.
10. Click **Set up source** and wait for the tests to complete.

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Google Cloud Storage (GCS) from the Source type dropdown.
4. Enter a name for the Google Cloud Storage (GCS) connector.
5. Select authorization type:
   1. **Authenticate via Google (OAuth)** from the Authentication dropdown, click **Sign in with Google** and complete the authentication workflow. 
   2. **Service Account Information** and paste the service account JSON key to the `Service Account Information` field .
6. Paste the service account JSON key to the `Service Account Information` field .
7. Enter your GCS bucket name to the `Bucket` field. 
8. Add a stream:
   1. Give a **Name** to the stream 
   2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below. 
   3. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
   4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
9. Configure the optional **Start Date** parameter that marks a starting date and time in UTC for data replication. Any files that have _not_ been modified since this specified date/time will _not_ be replicated. Use the provided datepicker (recommended) or enter the desired date programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. Leaving this field blank will replicate data from all files that have not been excluded by the **Path Pattern** and **Path Prefix**.
10. Click **Set up source** and wait for the tests to complete.

#### File urls

The Google Cloud Storage (GCS) source connector uses `signed url` to work with files when source authenticated with `Service Account Information` and `gs://{blob.bucket.name}/{blob.name}` when source authenticated via Google (OAuth).
This is important to know that File urls are used in the connection state. 
So if you change authorization type, and you use Incremental sync the next sync will not use old state and reread provided files in Full Refresh mode(like initial sync), next syncs will be Incremental as expected.

## Path Patterns

\(tl;dr -&gt; path pattern syntax using [wcmatch.glob](https://facelessuser.github.io/wcmatch/glob/). GLOBSTAR and SPLIT flags are enabled.\)

This connector can sync multiple files by using glob-style patterns, rather than requiring a specific path for every file. This enables:

- Referencing many files with just one pattern, e.g. `**` would indicate every file in the folder.
- Referencing future files that don't exist yet \(and therefore don't have a specific path\).

You must provide a path pattern. You can also provide many patterns split with \| for more complex directory layouts.

Each path pattern is a reference from the _root_ of the folder, so don't include the root folder name itself in the pattern\(s\).

Some example patterns:

- `**` : match everything.
- `**/*.csv` : match all files with specific extension.
- `myFolder/**/*.csv` : match all csv files anywhere under myFolder.
- `*/**` : match everything at least one folder deep.
- `*/*/*/**` : match everything at least three folders deep.
- `**/file.*|**/file` : match every file called "file" with any extension \(or no extension\).
- `x/*/y/*` : match all files that sit in sub-folder x -&gt; any folder -&gt; folder y.
- `**/prefix*.csv` : match all csv files with specific prefix.
- `**/prefix*.parquet` : match all parquet files with specific prefix.

Let's look at a specific example, matching the following folder layout (`MyFolder` is the folder specified in the connector config as the root folder, which the patterns are relative to):

```text
MyFolder
    -> log_files
    -> some_table_files
        -> part1.csv
        -> part2.csv
    -> images
    -> more_table_files
        -> part3.csv
    -> extras
        -> misc
            -> another_part1.csv
```

We want to pick up part1.csv, part2.csv and part3.csv \(excluding another_part1.csv for now\). We could do this a few different ways:

- We could pick up every csv file called "partX" with the single pattern `**/part*.csv`.
- To be a bit more robust, we could use the dual pattern `some_table_files/*.csv|more_table_files/*.csv` to pick up relevant files only from those exact folders.
- We could achieve the above in a single pattern by using the pattern `*table_files/*.csv`. This could however cause problems in the future if new unexpected folders started being created.
- We can also recursively wildcard, so adding the pattern `extras/**/*.csv` would pick up any csv files nested in folders below "extras", such as "extras/misc/another_part1.csv".

As you can probably tell, there are many ways to achieve the same goal with path patterns. We recommend using a pattern that ensures clarity and is robust against future additions to the directory structure.

## User Schema

When using the Avro, Jsonl, CSV or Parquet format, you can provide a schema to use for the output stream. **Note that this doesn't apply to the experimental Document file type format.**

Providing a schema allows for more control over the output of this stream. Without a provided schema, columns and datatypes will be inferred from the first created file in the bucket matching your path pattern and suffix. This will probably be fine in most cases but there may be situations you want to enforce a schema instead, e.g.:

- You only care about a specific known subset of the columns. The other columns would all still be included, but packed into the `_ab_additional_properties` map.
- Your initial dataset is quite small \(in terms of number of records\), and you think the automatic type inference from this sample might not be representative of the data in the future.
- You want to purposely define types for every column.
- You know the names of columns that will be added to future data and want to include these in the core schema as columns rather than have them appear in the `_ab_additional_properties` map.

Or any other reason! The schema must be provided as valid JSON as a map of `{"column": "datatype"}` where each datatype is one of:

- string
- number
- integer
- object
- array
- boolean
- null

For example:

- `{"id": "integer", "location": "string", "longitude": "number", "latitude": "number"}`
- `{"username": "string", "friends": "array", "information": "object"}`

## File Format Settings

### Avro

- **Convert Double Fields to Strings**: Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.

### CSV

Since CSV files are effectively plain text, providing specific reader options is often required for correct parsing of the files. These settings are applied when a CSV is created or exported so please ensure that this process happens consistently over time.

- **Header Definition**: How headers will be defined. `User Provided` assumes the CSV does not have a header row and uses the headers provided and `Autogenerated` assumes the CSV does not have a header row and the CDK will generate headers using for `f{i}` where `i` is the index starting from 0. Else, the default behavior is to use the header from the CSV file. If a user wants to autogenerate or provide column names for a CSV having headers, they can set a value for the "Skip rows before header" option to ignore the header row.
- **Delimiter**: Even though CSV is an acronym for Comma Separated Values, it is used more generally as a term for flat file data that may or may not be comma separated. The delimiter field lets you specify which character acts as the separator. To use [tab-delimiters](https://en.wikipedia.org/wiki/Tab-separated_values), you can set this value to `\t`. By default, this value is set to `,`.
- **Double Quote**: This option determines whether two quotes in a quoted CSV value denote a single quote in the data. Set to True by default.
- **Encoding**: Some data may use a different character set \(typically when different alphabets are involved\). See the [list of allowable encodings here](https://docs.python.org/3/library/codecs.html#standard-encodings). By default, this is set to `utf8`.
- **Escape Character**: An escape character can be used to prefix a reserved character and ensure correct parsing. A commonly used character is the backslash (`\`). For example, given the following data:

```
Product,Description,Price
Jeans,"Navy Blue, Bootcut, 34\"",49.99
```

The backslash (`\`) is used directly before the second double quote (`"`) to indicate that it is _not_ the closing quote for the field, but rather a literal double quote character that should be included in the value (in this example, denoting the size of the jeans in inches: `34"` ).

Leaving this field blank (default option) will disallow escaping.

- **False Values**: A set of case-sensitive strings that should be interpreted as false values.
- **Null Values**: A set of case-sensitive strings that should be interpreted as null values. For example, if the value 'NA' should be interpreted as null, enter 'NA' in this field.
- **Quote Character**: In some cases, data values may contain instances of reserved characters \(like a comma, if that's the delimiter\). CSVs can handle this by wrapping a value in defined quote characters so that on read it can parse it correctly. By default, this is set to `"`.
- **Skip Rows After Header**: The number of rows to skip after the header row.
- **Skip Rows Before Header**: The number of rows to skip before the header row.
- **Strings Can Be Null**: Whether strings can be interpreted as null values. If true, strings that match the null_values set will be interpreted as null. If false, strings that match the null_values set will be interpreted as the string itself.
- **True Values**: A set of case-sensitive strings that should be interpreted as true values.

### JSONL

- **Schemaless**: When enabled, syncs will not validate or structure records against the stream's schema.

### Parquet 

- **Convert Double Fields to Strings**: Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.

### Unstructured document format

- **Parsing Strategy**: The strategy used to parse documents. `fast` extracts text directly from the document which doesn't work for all files. `ocr_only` is more reliable, but slower. `hi_res` is the most reliable, but requires an API key and a hosted instance of unstructured and can't be used with local mode. See the [unstructured.io](https://unstructured-io.github.io/unstructured/core/partition.html#partition-pdf) documentation for more details.
- **Processing**: Processing configuration. Options:
  - Local - Process files locally, supporting `fast` and `ocr` modes. This is the default option.
  - Via API - Process files via an API, using the `hi_res` mode. This option is useful for increased performance and accuracy, but requires an API key and a hosted instance of unstructured.
- **Skip Unprocessable Files**: If true, skip files that cannot be parsed and pass the error message along as the _ab_source_file_parse_error field. If false, fail the sync.
- **Schemaless**: When enabled, syncs will not validate or structure records against the stream's schema.

### Excel

- **Schemaless**: When enabled, syncs will not validate or structure records against the stream's schema.

## Supported sync modes

The Google Cloud Storage (GCS) source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):


| Feature           | Supported?\(Yes/No\) | Notes |
|:------------------|:---------------------|:------|
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |

## Supported Streams

Google Cloud Storage (GCS) supports following file formats:
 - avro
 - jsonl
 - csv
 - parquet
 - unstructured document format
 - excel

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.8.7 | 2025-02-22 | [54458](https://github.com/airbytehq/airbyte/pull/54458) | Update dependencies |
| 0.8.6 | 2025-02-15 | [53712](https://github.com/airbytehq/airbyte/pull/53712) | Update dependencies |
| 0.8.5 | 2025-02-08 | [53365](https://github.com/airbytehq/airbyte/pull/53365) | Update dependencies |
| 0.8.4 | 2025-02-01 | [52379](https://github.com/airbytehq/airbyte/pull/52379) | Update dependencies |
| 0.8.3 | 2025-01-18 | [49174](https://github.com/airbytehq/airbyte/pull/49174) | Update dependencies |
| 0.8.2 | 2024-11-25 | [48647](https://github.com/airbytehq/airbyte/pull/48647) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.8.1 | 2024-10-28 | [45923](https://github.com/airbytehq/airbyte/pull/45923) | Update logging |
| 0.8.0 | 2024-10-28 | [45414](https://github.com/airbytehq/airbyte/pull/45414) | Add support for OAuth authentication |
| 0.7.4 | 2024-10-12 | [46858](https://github.com/airbytehq/airbyte/pull/46858) | Update dependencies |
| 0.7.3 | 2024-10-05 | [46458](https://github.com/airbytehq/airbyte/pull/46458) | Update dependencies |
| 0.7.2 | 2024-09-28 | [46178](https://github.com/airbytehq/airbyte/pull/46178) | Update dependencies |
| 0.7.1 | 2024-09-24 | [45850](https://github.com/airbytehq/airbyte/pull/45850) | Add integration tests |
| 0.7.0 | 2024-09-24 | [45671](https://github.com/airbytehq/airbyte/pull/45671) | Add .zip files support |
| 0.6.9 | 2024-09-21 | [45798](https://github.com/airbytehq/airbyte/pull/45798) | Update dependencies |
| 0.6.8 | 2024-09-19 | [45092](https://github.com/airbytehq/airbyte/pull/45092) | Update CDK v5; Fix OSError not raised in stream_reader.open_file |
| 0.6.7 | 2024-09-14 | [45492](https://github.com/airbytehq/airbyte/pull/45492) | Update dependencies |
| 0.6.6 | 2024-09-07 | [45232](https://github.com/airbytehq/airbyte/pull/45232) | Update dependencies |
| 0.6.5 | 2024-08-31 | [45010](https://github.com/airbytehq/airbyte/pull/45010) | Update dependencies |
| 0.6.4 | 2024-08-27 | [44796](https://github.com/airbytehq/airbyte/pull/44796) | Fix empty list of globs when prefix empty |
| 0.6.3 | 2024-08-26 | [44781](https://github.com/airbytehq/airbyte/pull/44781) | Set file signature URL expiration limit default to max |
| 0.6.2 | 2024-08-24 | [44733](https://github.com/airbytehq/airbyte/pull/44733) | Update dependencies |
| 0.6.1 | 2024-08-17 | [44285](https://github.com/airbytehq/airbyte/pull/44285) | Update dependencies |
| 0.6.0 | 2024-08-15 | [44015](https://github.com/airbytehq/airbyte/pull/44015) | Add support for all FileBasedSpec file types |
| 0.5.0 | 2024-08-14 | [44070](https://github.com/airbytehq/airbyte/pull/44070) | Update CDK v4 and Python 3.10 dependencies |
| 0.4.15 | 2024-08-12 | [43733](https://github.com/airbytehq/airbyte/pull/43733) | Update dependencies |
| 0.4.14 | 2024-08-10 | [43512](https://github.com/airbytehq/airbyte/pull/43512) | Update dependencies |
| 0.4.13 | 2024-08-03 | [43236](https://github.com/airbytehq/airbyte/pull/43236) | Update dependencies |
| 0.4.12 | 2024-07-27 | [42693](https://github.com/airbytehq/airbyte/pull/42693) | Update dependencies |
| 0.4.11 | 2024-07-20 | [42312](https://github.com/airbytehq/airbyte/pull/42312) | Update dependencies |
| 0.4.10 | 2024-07-13 | [41865](https://github.com/airbytehq/airbyte/pull/41865) | Update dependencies |
| 0.4.9 | 2024-07-10 | [41430](https://github.com/airbytehq/airbyte/pull/41430) | Update dependencies |
| 0.4.8 | 2024-07-09 | [41148](https://github.com/airbytehq/airbyte/pull/41148) | Update dependencies |
| 0.4.7 | 2024-07-06 | [41015](https://github.com/airbytehq/airbyte/pull/41015) | Update dependencies |
| 0.4.6 | 2024-06-26 | [40540](https://github.com/airbytehq/airbyte/pull/40540) | Update dependencies |
| 0.4.5 | 2024-06-25 | [40391](https://github.com/airbytehq/airbyte/pull/40391) | Update dependencies |
| 0.4.4 | 2024-06-24 | [40234](https://github.com/airbytehq/airbyte/pull/40234) | Update dependencies |
| 0.4.3 | 2024-06-22 | [40089](https://github.com/airbytehq/airbyte/pull/40089) | Update dependencies |
| 0.4.2 | 2024-06-06 | [39255](https://github.com/airbytehq/airbyte/pull/39255) | [autopull] Upgrade base image to v1.2.2 |
| 0.4.1 | 2024-05-29 | [38696](https://github.com/airbytehq/airbyte/pull/38696) | Avoid error on empty stream when running discover |
| 0.4.0 | 2024-03-21 | [36373](https://github.com/airbytehq/airbyte/pull/36373) | Add Gzip and Bzip compression support. Manage dependencies with Poetry. |
| 0.3.7 | 2024-02-06 | [34936](https://github.com/airbytehq/airbyte/pull/34936) | Bump CDK version to avoid missing SyncMode errors |
| 0.3.6 | 2024-01-30 | [34681](https://github.com/airbytehq/airbyte/pull/34681) | Unpin CDK version to make compatible with the Concurrent CDK |
| 0.3.5 | 2024-01-30 | [34661](https://github.com/airbytehq/airbyte/pull/34661) | Pin CDK version until upgrade for compatibility with the Concurrent CDK |
| 0.3.4 | 2024-01-11 | [34158](https://github.com/airbytehq/airbyte/pull/34158) | Fix issue in stream reader for document file type parser |
| 0.3.3 | 2023-12-06 | [33187](https://github.com/airbytehq/airbyte/pull/33187) | Bump CDK version to hide source-defined primary key |
| 0.3.2 | 2023-11-16 | [32608](https://github.com/airbytehq/airbyte/pull/32608) | Improve document file type parser |
| 0.3.1 | 2023-11-13 | [32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema |
| 0.3.0 | 2023-10-11 | [31212](https://github.com/airbytehq/airbyte/pull/31212) | Migrated to file based CDK |
| 0.2.0 | 2023-06-26 | [27725](https://github.com/airbytehq/airbyte/pull/27725) | License Update: Elv2 |
| 0.1.0 | 2023-02-16 | [23186](https://github.com/airbytehq/airbyte/pull/23186) | New Source: GCS |


</details>
