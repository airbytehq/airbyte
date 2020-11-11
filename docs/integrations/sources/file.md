# Files

## Overview

File are often exchanged or published in various remote locations. This source aims to support an expanding range of file formats and storage providers. The File source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the file and columns you set up for replication into the destination in a new table.

### Output schema

At this time, this source produces only a single stream for the target file as it replicates only one file at a time for the moment. We'll be considering to improve this behavior by globing folders or use patterns to capture more files in the next iterations as well as more file formats and storage providers.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| Replicate Folders \(multiple Files\) | No |
| Replicate Glob Patterns \(multiple Files\) | No |

### Storage Providers

| Storage Providers | Supported? |
| :--- | :--- |
| HTTPS | Yes |
| Google Cloud Storage | Yes |
| Amazon Web Services S3 | Yes |
| SFTP / SSH / SCP | Yes |
| WebHDFS | Untested |
| local filesystem | Untested |
| Azure Blob Storage | Untested \(hidden\) |
| HDFS | Untested \(hidden\) |

### File Formats

| Format | Supported? |
| :--- | :--- |
| CSV | Yes |
| JSON | experimental |
| HTML | Untested |
| Excel | Untested |
| Feather | Untested |
| Parquet | Untested |
| Orc | Untested |
| Pickle | Untested |

### Performance considerations

In order to read large files from a remote location, we are leveraging the capabilities of [smart\_open](https://pypi.org/project/smart-open/). However, for the `CSV` file format, it is possible to switch to either [GCSFS](https://gcsfs.readthedocs.io/en/latest/) or [S3FS](https://s3fs.readthedocs.io/en/latest/) implementations as it is natively supported by the `pandas` library. This choice is made possible through the optional `reader_impl` parameter.

### Limitations

* Note that for local filesystem, the file probably have to be stored somewhere in the `/tmp/airbyte_local` folder with the same limitations as the [CSV Destination](../destinations/local-csv.md). This may not be ideal as a Source and not well tested yet.
* The JSON implementation needs to be tweaked in order to produce more complex catalog and is still in an experimental state: Simple JSON schemas should work at this point but may not be well handled when there are multiple layers of nesting.

## Getting started

* Once the File Source is selected, you should define both the storage provider along its URL and format of the file.
* Depending on the choice made previously, more options may be necessary, especially when accessing private data.
* In case of GCS, it is necessary to provide the content of the service account keyfile to access private buckets. See settings of [BigQuery Destination](../destinations/bigquery.md)
* In case of AWS S3, the pair of `aws_access_key_id` and `aws_secret_access_key` is necessary to access private S3 buckets.

### Reader Options

The Reader in charge of loading the file format is currently based on [Pandas IO Tools](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html). It is possible to customize how to load the file into a Pandas DataFrame as part of this Source Connector. This is doable in the `reader_options` that should be in JSON format and depends on the chosen file format \(see panda's documentation, depending on the format\).

For example, if the format `CSV` is selected, then options from the [read\_csv](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-read-csv-table) functions are available.

* It is therefore possible to customize the `delimiter` \(or `sep`\) to `\t` in case of tab separated files.
* Header line can be ignored with `header=0` and customized with `names`
* etc

We would therefore provide in the `reader_options` the following json:

```text
{ "sep" : "\t", "header" : 0, "names": "column1, column2"}
```

In case you select `JSON` format, then options from the [read\_json](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-json-reader) reader are available.

For example, you can use the `{"orient" : "records"}` to change how orientation of data is loaded \(if data is `[{column -> value}, … , {column -> value}]`\)

