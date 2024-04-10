# Files (CSV, JSON, Excel, Feather, Parquet)

This page contains the setup guide and reference information for different files.

## Prerequisites

* A file hosted on AWS S3, GCS, HTTPS, an SFTP server, or locally

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes	 | No |
| Replicate Folders (multiple Files)	| No |
| Replicate Glob Patterns (multiple Files)	| No |
| Namespaces | No |

## Setup guide

### Step 1: Set up the source in Daspire

1. Select **Files (CSV, JSON, Excel, Feather, Parquet)** from the Source list.

2. Enter a **Source Name**.

3. For **Dataset Name**, enter the name of the final table to replicate this file into (should include letters, numbers, dashes and underscores only).

4. For **File Format**, select the format of the file to replicate from the dropdown menu (Warning: some formats may be experimental. Please refer to the table of supported formats below).

### Step 2: Select the provider and set provider-specific configurations

For **Storage Provider**, use the dropdown menu to select the Storage Provider or Location of the file(s) which should be replicated, then configure the provider-specific fields as needed:

#### HTTPS: Public Web [Default]

* User-Agent (Optional)

  Set this to active if you want to add the User-Agent header to requests (inactive by default).

#### GCS: Google Cloud Storage

* Service Account JSON (Required for private buckets)

  To access **private buckets** stored on Google Cloud, this integration requires a service account JSON credentials file with the appropriate permissions. A detailed breakdown of this topic can be found at the[Google Cloud service accounts page](https://cloud.google.com/iam/docs/service-accounts). Please generate the "credentials.json" file and copy its content to this field, ensuring it is in JSON format. If you are accessing **publicly available data**, this field is not required.

#### S3: Amazon Web Services

* AWS Access Key ID (Required for private buckets)
* AWS Secret Access Key (Required for private buckets)

  To access **private buckets** stored on AWS S3, this integration requires valid credentials with the necessary permissions. To access these keys, refer to the [AWS IAM documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). More information on setting permissions in AWS can be found [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html). If you are accessing **publicly available data**, these fields are not required.

#### AzBlob: Azure Blob Storage

* Storage Account (Required)

  This is the globally unique name of the storage account that the desired blob sits within. See the [Azure documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview) for more details.

  If you are accessing **private storage**, you must also provide one of the following security credentials with the necessary permissions:

  > * SAS Token: Find more information [here](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview).
  > * Shared Key: Find more information [here](https://learn.microsoft.com/en-us/rest/api/storageservices/authorize-with-shared-key).

#### SSH: Secure Shell / SCP: Secure Copy Protocol / SFTP: Secure File Transfer Protocol

* Host (Required)

  Enter the **hostname** or **IP address** of the remote server where the file trasfer will take place.

* User (Required)

  Enter the **username** associated with your account on the remote server.

* Password (Optional)

  If required by the remote server, enter the **password** associated with your user account. Otherwise, leave this field blank.

* Port (Optional)

  Specify the **port number number** to use for the connection. The default port is usually 22. However, if your remote server uses a non-standard port, you can enter the appropriate port number here.

#### Local Filesystem

* Storage

  > Note the local storage URL for reading must start with the local mount `/local/`.

  Please note that if you are replicating data from a locally stored file on Windows OS, you will need to open the `.env` file in your local Daspire root folder and change the values for:

  > * `LOCAL_ROOT`
  > * `LOCAL_DOCKER_MOUNT`
  > * `HACK_LOCAL_ROOT_PARENT`

  Please set these to an existing absolute path on your machine. Colons in the path need to be replaced with a double forward slash, `//`. `LOCAL_ROOT` & `LOCAL_DOCKER_MOUNT` should be set to the same value, and `HACK_LOCAL_ROOT_PARENT` should be set to their parent directory.

### Step 3: Select the provider and set provider-specific configurations

1. For **URL**, enter the URL path of the file to be replicated.

  > When connecting to a file located in **Google Drive**, please note that you need to utilize the Download URL format: *https://drive.google.com/uc?export=download&id=[DRIVE_FILE_ID]*. `[DRIVE_FILE_ID]` should be replaced with the unique string found in the Share URL specific to Google Drive. You can find the Share URL by visiting *https://drive.google.com/file/d/[DRIVE_FILE_ID]/view?usp=sharing*.

  > When connecting to a file using **Azure Blob Storage**, please note that we account for the base URL. Therefore, you should only need to include the path to your specific file (eg `container/file.csv`).

2. For **Reader Options** (Optional), you may choose to enter a string in JSON format. Depending on the file format of your source, this will provide additional options and tune the Reader's behavior. Please refer to the next section for a breakdown of the possible inputs. This field may be left blank if you do not wish to configure custom Reader options.

  > Normally, Daspire tries to infer the data type from the source, but you can use `reader_options` to force specific data types. If you input `{"dtype":"string"}`, all columns will be forced to be parsed as strings. If you only want a specific column to be parsed as a string, simply use `{"dtype" : {"column name": "string"}}`.

3. Click **Save & Test**.

## Reader options

The Reader in charge of loading the file format is currently based on [Pandas IO Tools](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html). It is possible to customize how to load the file into a Pandas DataFrame as part of this Source. This is doable in the `reader_options` that should be in JSON format and depends on the chosen file format. See pandas' documentation, depending on the format:

For example, if the format `CSV` is selected, then options from the [read_csv](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-read-csv-table) functions are available.

* It is therefore possible to customize the delimiter (or sep) to in case of tab separated files.
* Header line can be ignored with header=0 and customized with names
* Parse dates for in specified columns

We would therefore provide in the `reader_options` the following json:

```
{ "sep" : "\t", "header" : 0, "names": ["column1", "column2"], "parse_dates": ["column2"]}
```
In case you select `JSON` format, then options from the [read_json](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-json-reader) reader are available.

For example, you can use the `{"orient" : "records"}` to change how orientation of data is loaded (if data is `[{column -> value}, … , {column -> value}]`)

If you need to read Excel Binary Workbook, please specify `excel_binary` format in `File Format` select.

## Supported File / Stream Compression

| Compression | Supported? |
| --- | --- |
| Gzip | Yes |
| Zip | No |
| Bzip2	 | No |
| Lzma	| No |
| Xz	| No |
| Snappy | No |

## Supported Storage Providers

| Storage Providers | Supported? |
| --- | --- |
| HTTPS | Yes |
| Google Cloud Storage | Yes |
| Amazon Web Services S3 | Yes |
| SFTP	| Yes |
| SSH / SCP		| Yes |
| local filesystem	 | Yes |

## Supported File Formats

| Format | Supported? |
| --- | --- |
| CSV | Yes |
| JSON/JSONL | Yes |
| HTML | No |
| XML	| No |
| Excel	| Yes |
| Excel Binary Workbook	| Yes |
| Feather | Yes |
| Parquet	| Yes |
| Pickle | No |
| YAML	| Yes |

## Data type mapping

The Stripe API uses the same [JSON Schema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Daspire uses internally (string, date-time, object, array, boolean, integer, and number), so no type conversions are performed for the Stripe integration.

## Performance Considerations and Notes

In order to read large files from a remote location, this connector uses the [smart_open](https://pypi.org/project/smart-open/) library. However, it is possible to switch to either [GCSFS](https://gcsfs.readthedocs.io/en/latest/) or [S3FS](https://s3fs.readthedocs.io/en/latest/) implementations as it is natively supported by the pandas library. This choice is made possible through the optional `reader_impl` parameter.

* Note that for local filesystem, the file probably have to be stored somewhere in the `/tmp/daspire_local` folder, so the `URL` should also starts with `/local/`.

* Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the **"Apply & restart"** button.

* The JSON implementation needs to be tweaked in order to produce more complex catalog and is still in an experimental state: Simple JSON schemas should work at this point but may not be well handled when there are multiple layers of nesting.
