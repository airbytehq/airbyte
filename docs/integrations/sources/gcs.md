# GCS

This page guides you through the process of setting up the GCS source connector. This connector supports loading multiple CSV files (non compressed) from a GCS directory. The conntector will check for all files ending in `.csv`, even nested files.

:::info
Cloud storage may incur egress costs. Egress refers to data that is transferred out of the cloud storage system, such as when you download files or access them from a different location. For more information, see the [Google Cloud Storage pricing guide](https://cloud.google.com/storage/pricing).
:::

## Prerequisites

- JSON credentials for the service account that has access to GCS. For more details check [instructions](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
- GCS bucket
- Path to file(s)

## Set up Source

### Create a Service Account

First, you need to select existing or create a new project in the Google Cloud Console:

1. Sign in to the Google Account.
2. Go to the [Service Accounts](https://console.developers.google.com/iam-admin/serviceaccounts) page.
3. Click `Create service account`.
4. Create a JSON key file for the service user. The contents of this file will be provided as the `service_account` in the UI.

### Grant permisison to GCS

Use the service account ID from above, grant read access to your target bucket. Click [here](https://cloud.google.com/storage/docs/access-control/using-iam-permissions) for more details.

### Set up the source in Airbyte UI

- Paste the service account JSON key to the `Service Account Information` field
- Enter your GCS bucket name to the `Bucket` field
- Add a stream
  1.  Give a **Name** to the stream
  2.  In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported format is **CSV**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
  3.  Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
  4.  (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
- Configure the optional **Start Date** parameter that marks a starting date and time in UTC for data replication. Any files that have _not_ been modified since this specified date/time will _not_ be replicated. Use the provided datepicker (recommended) or enter the desired date programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. Leaving this field blank will replicate data from all files that have not been excluded by the **Path Pattern** and **Path Prefix**.
- Click **Set up source** and wait for the tests to complete.

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

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.4.1   | 2024-05-29 | [38696](https://github.com/airbytehq/airbyte/pull/38696) | Avoid error on empty stream when running discover                       |
| 0.4.0   | 2024-03-21 | [36373](https://github.com/airbytehq/airbyte/pull/36373) | Add Gzip and Bzip compression support. Manage dependencies with Poetry. |
| 0.3.7   | 2024-02-06 | [34936](https://github.com/airbytehq/airbyte/pull/34936) | Bump CDK version to avoid missing SyncMode errors                       |
| 0.3.6   | 2024-01-30 | [34681](https://github.com/airbytehq/airbyte/pull/34681) | Unpin CDK version to make compatible with the Concurrent CDK            |
| 0.3.5   | 2024-01-30 | [34661](https://github.com/airbytehq/airbyte/pull/34661) | Pin CDK version until upgrade for compatibility with the Concurrent CDK |
| 0.3.4   | 2024-01-11 | [34158](https://github.com/airbytehq/airbyte/pull/34158) | Fix issue in stream reader for document file type parser                |
| 0.3.3   | 2023-12-06 | [33187](https://github.com/airbytehq/airbyte/pull/33187) | Bump CDK version to hide source-defined primary key                     |
| 0.3.2   | 2023-11-16 | [32608](https://github.com/airbytehq/airbyte/pull/32608) | Improve document file type parser                                       |
| 0.3.1   | 2023-11-13 | [32357](https://github.com/airbytehq/airbyte/pull/32357) | Improve spec schema                                                     |
| 0.3.0   | 2023-10-11 | [31212](https://github.com/airbytehq/airbyte/pull/31212) | Migrated to file based CDK                                              |
| 0.2.0   | 2023-06-26 | [27725](https://github.com/airbytehq/airbyte/pull/27725) | License Update: Elv2                                                    |
| 0.1.0   | 2023-02-16 | [23186](https://github.com/airbytehq/airbyte/pull/23186) | New Source: GCS                                                         |

</details>