# Google Drive

This page contains the setup guide and reference information for the Google Drive source connector.

:::info
The Google Drive source connector pulls data from a single folder in Google Drive. Subfolders are recursively included in the sync. All files in the specified folder and all sub folders will be considered.
:::

## Prerequisites

- Drive folder link - The link to the Google Drive folder you want to sync files from (includes files located in subfolders)
<!-- env:cloud -->
- **For Airbyte Cloud** A Google Workspace user with access to the spreadsheet
  <!-- /env:cloud -->
  <!-- env:oss -->
- **For Airbyte Open Source:**
  - A GCP project
  - Enable the Google Drive API in your GCP project
  - Service Account Key with access to the Spreadsheet you want to replicate
  <!-- /env:oss -->

## Setup guide

The Google Drive source connector supports authentication via either OAuth or Service Account Key Authentication.

<!-- env:cloud -->

For **Airbyte Cloud** users, we highly recommend using OAuth, as it significantly simplifies the setup process and allows you to authenticate [directly from the Airbyte UI](#set-up-the-google-drive-source-connector-in-airbyte).

<!-- /env:cloud -->

<!-- env:oss -->

For **Airbyte Open Source** users, we recommend using Service Account Key Authentication. Follow the steps below to create a service account, generate a key, and enable the Google Drive API.

:::note
If you prefer to use OAuth for authentication with **Airbyte Open Source**, you can follow [Google's OAuth instructions](https://developers.google.com/identity/protocols/oauth2) to create an authentication app. Be sure to set the scopes to `https://www.googleapis.com/auth/drive.readonly`. You will need to obtain your client ID, client secret, and refresh token for the connector setup.
:::

### Set up the service account key (Airbyte Open Source)

#### Create a service account

1. Open the [Service Accounts page](https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts) in your Google Cloud console.
2. Select an existing project, or create a new project.
3. At the top of the page, click **+ Create service account**.
4. Enter a name and description for the service account, then click **Create and Continue**.
5. Under **Service account permissions**, select the roles to grant to the service account, then click **Continue**. We recommend the **Viewer** role.

#### Generate a key

1. Go to the [API Console/Credentials](https://console.cloud.google.com/apis/credentials) page and click on the email address of the service account you just created.
2. In the **Keys** tab, click **+ Add key**, then click **Create new key**.
3. Select **JSON** as the Key type. This will generate and download the JSON key file that you'll use for authentication. Click **Continue**.

#### Enable the Google Drive API

1. Go to the [API Console/Library](https://console.cloud.google.com/apis/library) page.
2. Make sure you have selected the correct project from the top.
3. Find and select the **Google Drive API**.
4. Click **ENABLE**.

If your folder is viewable by anyone with its link, no further action is needed. If not, give your Service account access to your folder. Check out [this video](https://youtu.be/GyomEw5a2NQ%22) for how to do this.

<!-- /env:oss -->

### Set up the Google Drive source connector in Airbyte

To set up Google Drive as a source in Airbyte Cloud:

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Drive** from the list of available sources.
4. For **Source name**, enter a name to help you identify this source.
5. Select your authentication method:

<!-- env:cloud -->

#### For Airbyte Cloud

- **(Recommended)** Select **Authenticate via Google (OAuth)** from the Authentication dropdown, click **Sign in with Google** and complete the authentication workflow.

<!-- /env:cloud -->
<!-- env:oss -->

#### For Airbyte Open Source

- **(Recommended)** Select **Service Account Key Authentication** from the dropdown and enter your Google Cloud service account key in JSON format:

  ```js
  { "type": "service_account", "project_id": "YOUR_PROJECT_ID", "private_key_id": "YOUR_PRIVATE_KEY", ... }
  ```

- To authenticate your Google account via OAuth, select **Authenticate via Google (OAuth)** from the dropdown and enter your Google application's client ID, client secret, and refresh token.

<!-- /env:oss -->

6. For **Folder Link**, enter the link to the Google Drive folder. To get the link, navigate to the folder you want to sync in the Google Drive UI, and copy the current URL.
7. Configure the optional **Start Date** parameter that marks a starting date and time in UTC for data replication. Any files that have _not_ been modified since this specified date/time will _not_ be replicated. Use the provided datepicker (recommended) or enter the desired date programmatically in the format `YYYY-MM-DDTHH:mm:ssZ`. Leaving this field blank will replicate data from all files that have not been excluded by the **Path Pattern** and **Path Prefix**.
8. Click **Set up source** and wait for the tests to complete.

## Supported sync modes

The Google Drive source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                                        | Supported? |
| :--------------------------------------------- | :--------- |
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files \(pattern matching\)  | Yes        |
| Replicate Multiple Streams \(distinct tables\) | Yes        |
| Namespaces                                     | No         |

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

#### Parsing via Unstructured.io Python Library

This connector utilizes the open source [Unstructured](https://unstructured-io.github.io/unstructured/introduction.html#product-offerings) library to perform OCR and text extraction from PDFs and MS Word files, as well as from embedded tables and images. You can read more about the parsing logic in the [Unstructured docs](https://unstructured-io.github.io/unstructured/core/partition.html) and you can learn about other Unstructured tools and services at [www.unstructured.io](https://www.unstructured.io).

#### Copy Raw Files Configuration

<FieldAnchor field="delivery_method.delivery_type">

:::info

The raw file replication feature has the following requirements and limitations:
- **Supported Airbyte Versions:**
  - Cloud: All Workspaces
  - OSS / Enterprise: `v1.2.0` or later
- **Max File Size:** `1GB` per file
- **Supported Destinations:**
  - S3: `v1.4.0` or later

:::

Copy raw files without parsing their contents. Bits are copied into the destination exactly as they appeared in the source. Recommended for use with unstructured text data, non-text and compressed files.

Format options will not be taken into account. Instead, files will be transferred to the file-based destination without parsing underlying data.

</FieldAnchor>

##### Preserve Sub-Directories in File Paths

If enabled, sends subdirectory folder structure along with source file names to the destination. Otherwise, files will be synced by their names only. This option is ignored when file-based replication is not enabled.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                      |
|---------|------------|----------------------------------------------------------|----------------------------------------------------------------------------------------------|
| 0.2.0 | 2025-02-28 | [52099](https://github.com/airbytehq/airbyte/pull/52099) | Add ACL and Identities options |
| 0.1.1 | 2025-02-01 | [43895](https://github.com/airbytehq/airbyte/pull/43895) | Update dependencies |
| 0.1.0 | 2025-01-27 | [52572](https://github.com/airbytehq/airbyte/pull/52572) | Promoting release candidate 0.1.0-rc.1 to a main version. |
| 0.1.0-rc.1  | 2025-01-20 | [51585](https://github.com/airbytehq/airbyte/pull/51585) | Bump cdk to enable universal file transfer |
| 0.0.12 | 2024-06-06 | [39291](https://github.com/airbytehq/airbyte/pull/39291) | [autopull] Upgrade base image to v1.2.2 |
| 0.0.11 | 2024-05-29 | [38698](https://github.com/airbytehq/airbyte/pull/38698) | Avoid error on empty stream when running discover |
| 0.0.10 | 2024-03-28 | [36581](https://github.com/airbytehq/airbyte/pull/36581) | Manage dependencies with Poetry |
| 0.0.9 | 2024-02-06 | [34936](https://github.com/airbytehq/airbyte/pull/34936) | Bump CDK version to avoid missing SyncMode errors |
| 0.0.8 | 2024-01-30 | [34681](https://github.com/airbytehq/airbyte/pull/34681) | Unpin CDK version to make compatible with the Concurrent CDK |
| 0.0.7 | 2024-01-30 | [34661](https://github.com/airbytehq/airbyte/pull/34661) | Pin CDK version until upgrade for compatibility with the Concurrent CDK |
| 0.0.6 | 2023-12-16 | [33414](https://github.com/airbytehq/airbyte/pull/33414) | Prepare for airbyte-lib |
| 0.0.5 | 2023-12-14 | [33411](https://github.com/airbytehq/airbyte/pull/33411) | Bump CDK version to auto-set primary key for document file streams and support raw txt files |
| 0.0.4 | 2023-12-06 | [33187](https://github.com/airbytehq/airbyte/pull/33187) | Bump CDK version to hide source-defined primary key |
| 0.0.3 | 2023-11-16 | [31458](https://github.com/airbytehq/airbyte/pull/31458) | Improve folder id input and update document file type parser |
| 0.0.2 | 2023-11-02 | [31458](https://github.com/airbytehq/airbyte/pull/31458) | Allow syncs on shared drives |
| 0.0.1 | 2023-11-02 | [31458](https://github.com/airbytehq/airbyte/pull/31458) | Initial Google Drive source |

</details>
