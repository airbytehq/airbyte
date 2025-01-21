# Microsoft OneDrive

This page contains the setup guide and reference information for the Microsoft OneDrive source connector.

### Requirements

- Application \(client\) ID
- Directory \(tenant\) ID
- Drive name
- Folder Path
- Client secrets

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Microsoft OneDrive** from the Source type dropdown.
4. Enter the name for the Microsoft OneDrive connector.
5. Enter **Drive Name**. To find your drive name go to settings and at the top of setting menu you can find the name of your drive.
6. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
7. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
8. The **OAuth2.0** authorization method is selected by default. Click **Authenticate your Microsoft OneDrive account**. Log in and authorize your Microsoft account.
9. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
10. Add a stream:
    1. Write the **File Type**
    2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
    3. Give a **Name** to the stream
    4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
    5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
11. Click **Set up source**
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

### Step 1: Set up OneDrive application

The Microsoft Graph API uses OAuth for authentication. Microsoft Graph exposes granular permissions that control the access that apps have to resources, like users, groups, and mail. When a user signs in to your app they, or, in some cases, an administrator, are given a chance to consent to these permissions. If the user consents, your app is given access to the resources and APIs that it has requested. For apps that don't take a signed-in user, permissions can be pre-consented to by an administrator when the app is installed.

Microsoft Graph has two types of permissions:

- **Delegated permissions** are used by apps that have a signed-in user present. For these apps, either the user or an administrator consents to the permissions that the app requests, and the app can act as the signed-in user when making calls to Microsoft Graph. Some delegated permissions can be consented by non-administrative users, but some higher-privileged permissions require administrator consent.
- **Application permissions** are used by apps that run without a signed-in user present; for example, apps that run as background services or daemons. Application permissions can only be consented by an administrator.

This source requires **Application permissions**. Follow these [instructions](https://docs.microsoft.com/en-us/graph/auth-v2-service?context=graph%2Fapi%2F1.0&view=graph-rest-1.0) for creating an app in the Azure portal. This process will produce the `client_id`, `client_secret`, and `tenant_id` needed for the tap configuration file.

1. Login to [Azure Portal](https://portal.azure.com/#home)
2. Click upper-left menu icon and select **Azure Active Directory**
3. Select **App Registrations**
4. Click **New registration**
5. Register an application
   1. Name:
   2. Supported account types: Accounts in this organizational directory only
   3. Register \(button\)
6. Record the client_id and tenant_id which will be used by the tap for authentication and API integration.
7. Select **Certificates & secrets**
8. Provide **Description and Expires**
   1. Description: tap-microsoft-onedrive client secret
   2. Expires: 1-year
   3. Add
9. Copy the client secret value, this will be the client_secret
10. Select **API permissions**
    1. Click **Add a permission**
11. Select **Microsoft Graph**
12. Select **Application permissions**
13. Select the following permissions:
    1. Files
       - Files.Read.All
14. Click **Add permissions**
15. Click **Grant admin consent**

### Step 2: Set up the Microsoft OneDrive connector in Airbyte

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up** the source page, select **Microsoft OneDrive** from the Source type dropdown.
4. Enter the name for the Microsoft OneDrive connector.
5. Enter **Drive Name**. To find your drive name go to settings and at the top of setting menu you can find the name of your drive.
6. Select **Search Scope**. Specifies the location(s) to search for files. Valid options are 'ACCESSIBLE_DRIVES' to search in the selected OneDrive drive, 'SHARED_ITEMS' for shared items the user has access to, and 'ALL' to search both. Default value is 'ALL'.
7. Enter **Folder Path**. Leave empty to search all folders of the drives. This does not apply to shared items.
8. Switch to **Service Key Authentication**
9. For **User Practical Name**, enter the [UPN](https://learn.microsoft.com/en-us/sharepoint/list-onedrive-urls) for your user.
10. Enter **Tenant ID**, **Client ID** and **Client secret**.
11. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
12. Add a stream:
    1. Write the **File Type**
    2. In the **Format** box, use the dropdown menu to select the format of the files you'd like to replicate. The supported formats are **CSV**, **Parquet**, **Avro** and **JSONL**. Toggling the **Optional fields** button within the **Format** box will allow you to enter additional configurations based on the selected format. For a detailed breakdown of these settings, refer to the [File Format section](#file-format-settings) below.
    3. Give a **Name** to the stream
    4. (Optional) - If you want to enforce a specific schema, you can enter a **Input schema**. By default, this value is set to `{}` and will automatically infer the schema from the file\(s\) you are replicating. For details on providing a custom schema, refer to the [User Schema section](#user-schema).
    5. Optionally, enter the **Globs** which dictates which files to be synced. This is a regular expression that allows Airbyte to pattern match the specific files to replicate. If you are replicating all the files within your bucket, use `**` as the pattern. For more precise pattern matching options, refer to the [Path Patterns section](#path-patterns) below.
13. Click **Set up source**

<!-- /env:oss -->

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

### Parquet

Apache Parquet is a column-oriented data storage format of the Apache Hadoop ecosystem. It provides efficient data compression and encoding schemes with enhanced performance to handle complex data in bulk. At the moment, partitioned parquet datasets are unsupported. The following settings are available:

- **Convert Decimal Fields to Floats**: Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.

### Avro

The Avro parser uses the [Fastavro library](https://fastavro.readthedocs.io/en/latest/). The following settings are available:

- **Convert Double Fields to Strings**: Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.

### JSONL

There are currently no options for JSONL parsing.

### Document File Type Format (Experimental)

:::warning
The Document file type format is currently an experimental feature and not subject to SLAs. Use at your own risk.
:::

The Document file type format is a special format that allows you to extract text from Markdown, TXT, PDF, Word, Powerpoint and Google documents. If selected, the connector will extract text from the documents and output it as a single field named `content`. The `document_key` field will hold a unique identifier for the processed file which can be used as a primary key. The content of the document will contain markdown formatting converted from the original file format. Each file matching the defined glob pattern needs to either be a markdown (`md`), PDF (`pdf`) or Docx (`docx`) file.

One record will be emitted for each document. Keep in mind that large files can emit large records that might not fit into every destination as each destination has different limitations for string fields.

Before parsing each document, the connector exports Google Document files to Docx format internally. Google Sheets, Google Slides, and drawings are internally exported and parsed by the connector as PDFs.

## Sync overview

### Data type mapping

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

### Features

| Feature           | Supported?\(Yes/No\) |
| :---------------- | :------------------- |
| Full Refresh Sync | Yes                  |
| Incremental Sync  | Yes                  |

### Performance considerations

The connector is restricted by normal Microsoft Graph [requests limitation](https://docs.microsoft.com/en-us/graph/throttling).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| 0.2.21 | 2024-10-12 | [46177](https://github.com/airbytehq/airbyte/pull/46177) | Update dependencies |
| 0.2.20 | 2024-09-21 | [45728](https://github.com/airbytehq/airbyte/pull/45728) | Update dependencies |
| 0.2.19 | 2024-09-14 | [45583](https://github.com/airbytehq/airbyte/pull/45583) | Update dependencies |
| 0.2.18 | 2024-09-07 | [45312](https://github.com/airbytehq/airbyte/pull/45312) | Update dependencies |
| 0.2.17 | 2024-08-31 | [45048](https://github.com/airbytehq/airbyte/pull/45048) | Update dependencies |
| 0.2.16 | 2024-08-24 | [44699](https://github.com/airbytehq/airbyte/pull/44699) | Update dependencies |
| 0.2.15 | 2024-08-12 | [43799](https://github.com/airbytehq/airbyte/pull/43799) | Update dependencies |
| 0.2.14 | 2024-08-10 | [43538](https://github.com/airbytehq/airbyte/pull/43538) | Update dependencies |
| 0.2.13 | 2024-08-03 | [43168](https://github.com/airbytehq/airbyte/pull/43168) | Update dependencies |
| 0.2.12 | 2024-07-27 | [42630](https://github.com/airbytehq/airbyte/pull/42630) | Update dependencies |
| 0.2.11 | 2024-07-20 | [42175](https://github.com/airbytehq/airbyte/pull/42175) | Update dependencies |
| 0.2.10 | 2024-07-13 | [41764](https://github.com/airbytehq/airbyte/pull/41764) | Update dependencies |
| 0.2.9 | 2024-07-10 | [41366](https://github.com/airbytehq/airbyte/pull/41366) | Update dependencies |
| 0.2.8 | 2024-07-09 | [41213](https://github.com/airbytehq/airbyte/pull/41213) | Update dependencies |
| 0.2.7 | 2024-06-29 | [40623](https://github.com/airbytehq/airbyte/pull/40623) | Update dependencies |
| 0.2.6 | 2024-06-26 | [40534](https://github.com/airbytehq/airbyte/pull/40534) | Update dependencies |
| 0.2.5 | 2024-06-25 | [40506](https://github.com/airbytehq/airbyte/pull/40506) | Update dependencies |
| 0.2.4 | 2024-06-23 | [40226](https://github.com/airbytehq/airbyte/pull/40226) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40160](https://github.com/airbytehq/airbyte/pull/40160) | Update dependencies |
| 0.2.2 | 2024-06-06 | [39227](https://github.com/airbytehq/airbyte/pull/39227) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-29 | [38676](https://github.com/airbytehq/airbyte/pull/38676) | Avoid error on empty stream when running discover |
| 0.2.0 | 2024-03-12 | [35849](https://github.com/airbytehq/airbyte/pull/35849) | Add fetching shared items |
| 0.1.9 | 2024-03-11 | [35956](https://github.com/airbytehq/airbyte/pull/35956) | Pin `transformers` transitive dependency |
| 0.1.8 | 2024-03-06 | [35858](https://github.com/airbytehq/airbyte/pull/35858) | Bump poetry.lock to upgrade transitive dependency |
| 0.1.7 | 2024-03-04 | [35584](https://github.com/airbytehq/airbyte/pull/35584) | Enable in Cloud |
| 0.1.6 | 2024-02-06 | [34936](https://github.com/airbytehq/airbyte/pull/34936) | Bump CDK version to avoid missing SyncMode errors |
| 0.1.5 | 2024-01-30 | [34681](https://github.com/airbytehq/airbyte/pull/34681) | Unpin CDK version to make compatible with the Concurrent CDK |
| 0.1.4 | 2024-01-30 | [34661](https://github.com/airbytehq/airbyte/pull/34661) | Pin CDK version until upgrade for compatibility with the Concurrent CDK |
| 0.1.3 | 2024-01-24 | [34478](https://github.com/airbytehq/airbyte/pull/34478) | Fix OAuth |
| 0.1.2 | 2021-12-22 | [33745](https://github.com/airbytehq/airbyte/pull/33745) | Add ql and sl to metadata |
| 0.1.1 | 2021-12-15 | [33758](https://github.com/airbytehq/airbyte/pull/33758) | Fix for docs name |
| 0.1.0 | 2021-12-06 | [32655](https://github.com/airbytehq/airbyte/pull/32655) | New source |

</details>
