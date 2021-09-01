# Files

## Overview

File are often exchanged or published in various remote locations. This source aims to support an expanding range of file formats and storage providers. The File source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the file and columns you set up for replication into the destination in a new table.

### Output schema

At this time, this source produces only a single stream for the target file as it replicates only one file at a time for the moment. We'll be considering to improve this behavior by globing folders or use patterns to capture more files in the next iterations as well as more file formats and storage providers. Note that you should provide the `dataset_name` which dictates how the table will be identified in the destination \(since `URL` can be made of complex characters\)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| Replicate Folders \(multiple Files\) | No |
| Replicate Glob Patterns \(multiple Files\) | No |
| Namespaces | No |

How do we rate the functionalities below?

* Yes, means we verified and have Automated Integration Tests for it.
* Verified, means we don't have Automated Tests but were able to successfully manually test and use it with Airbyte.
* Experimental, means we tried to verify but we may have ran into edge cases that still need to be addressed to be usable, please use with cautions.
* Untested, means the library we are using claims to support such configurations in theory but we haven't tested or verified that's it's working in Airbyte yet.
* Hidden, means that we haven't tested or even hooked up the options all the way to the UI yet.

Please, don't hesitate to get in touch with us and/or provide usage feedbacks if you are able to report issues, verify, contribute some testing or even suggest an option that is not part of these list, thanks!

### Storage Providers

Storage Providers are mostly enabled \(and further tested\) thanks to other open-source libraries that we are using under the hood such as:

* [smart\_open](https://pypi.org/project/smart-open/)
* [paramiko](http://docs.paramiko.org/en/stable/)
* [GCSFS](https://gcsfs.readthedocs.io/en/latest/)
* [S3FS](https://s3fs.readthedocs.io/en/latest/)

| Storage Providers | Supported? |
| :--- | :--- |
| HTTPS | Yes |
| Google Cloud Storage | Yes |
| Amazon Web Services S3 | Yes |
| SFTP | Yes |
| SSH / SCP | Yes |
| local filesystem | Experimental |

### File / Stream Compression

| Compression | Supported? |
| :--- | :--- |
| Gzip | Yes |
| Zip | No |
| Bzip2 | No |
| Lzma | No |
| Xz | No |
| Snappy | No |

### File Formats

File Formats are mostly enabled \(and further tested\) thanks to other open-source libraries that we are using under the hood such as:

* [Pandas IO Tools](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html)

| Format | Supported? |
| :--- | :--- |
| CSV | Yes |
| JSON | Yes |
| HTML | No |
| XML | No |
| Excel | Yes |
| Excel Binary Workbook| Yes |
| Feather | Yes |
| Parquet | Yes |
| Pickle | No |

### Performance considerations

In order to read large files from a remote location, we are leveraging the capabilities of [smart\_open](https://pypi.org/project/smart-open/). However, it is possible to switch to either [GCSFS](https://gcsfs.readthedocs.io/en/latest/) or [S3FS](https://s3fs.readthedocs.io/en/latest/) implementations as it is natively supported by the `pandas` library. This choice is made possible through the optional `reader_impl` parameter.

### Limitations / Experimentation notes

* Note that for local filesystem, the file probably have to be stored somewhere in the `/tmp/airbyte_local` folder with the same limitations as the [CSV Destination](../destinations/local-csv.md) so the `URL` should also starts with `/local/`. This may not be ideal as a Source but will probably evolve later.
* The JSON implementation needs to be tweaked in order to produce more complex catalog and is still in an experimental state: Simple JSON schemas should work at this point but may not be well handled when there are multiple layers of nesting.

## Getting started

* Once the File Source is selected, you should define both the storage provider along its URL and format of the file.
* Depending on the choice made previously, more options may be necessary, especially when accessing private data.
* In case of GCS, it is necessary to provide the content of the service account keyfile to access private buckets. See settings of [BigQuery Destination](../destinations/bigquery.md)
* In case of AWS S3, the pair of `aws_access_key_id` and `aws_secret_access_key` is necessary to access private S3 buckets.
* In case of AzBlob, it is necessary to provide the `storage_account` in which the blob you want to access resides. Either `sas_token` [(info)](https://docs.microsoft.com/en-us/azure/storage/blobs/sas-service-create?tabs=dotnet) or `shared_key` [(info)](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal) is necessary to access private blobs.

### Reader Options

The Reader in charge of loading the file format is currently based on [Pandas IO Tools](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html). It is possible to customize how to load the file into a Pandas DataFrame as part of this Source Connector. This is doable in the `reader_options` that should be in JSON format and depends on the chosen file format. See panda's documentation, depending on the format:

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

#### Changing data types of source columns

Normally, Airbyte tries to infer the data type from the source, but you can use `reader_options` to force specific data types. If you input `{"dtype":"string"}`, all columns will be forced to be parsed as strings. If you only want a specific column to be parsed as a string, simply use `{"dtype" : {"column name": "string"}}`. 

### Examples

Here are a list of examples of possible file inputs:

| Dataset Name | Storage | URL | Reader Impl | Service Account | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| epidemiology | HTTPS | [https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv](https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv) |  |  | [COVID-19 Public dataset](https://console.cloud.google.com/marketplace/product/bigquery-public-datasets/covid19-public-data-program?filter=solution-type:dataset&id=7d6cc408-53c8-4485-a187-b8cb9a5c0b56) on BigQuery |
| hr\_and\_financials | GCS | gs://airbyte-vault/financial.csv | smart\_open or gcfs | {"type": "service\_account", "private\_key\_id": "XXXXXXXX", ...} | data from a private bucket, a service account is necessary |
| landsat\_index | GCS | gcp-public-data-landsat/index.csv.gz | smart\_open |  | Using smart\_open, we don't need to specify the compression \(note the gs:// is optional too, same for other providers\) |

Examples with reader options:

| Dataset Name | Storage | URL | Reader Impl | Reader Options | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| landsat\_index | GCS | gs://gcp-public-data-landsat/index.csv.gz | GCFS | {"compression": "gzip"} | Additional reader options to specify a compression option to `read_csv` |
| GDELT | S3 | s3://gdelt-open-data/events/20190914.export.csv |  | {"sep": "\t", "header": null} | Here is TSV data separated by tabs without header row from [AWS Open Data](https://registry.opendata.aws/gdelt/) |
| server\_logs | local | /local/logs.log |  | {"sep": ";"} | After making sure a local text file exists at `/tmp/airbyte_local/logs.log` with logs file from some server that are delimited by ';' delimiters |

Example for SFTP:

| Dataset Name | Storage | User | Password | Host | URL | Reader Options | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Test Rebext | SFTP | demo | password | test.rebext.net | /pub/example/readme.txt | {"sep": "\r\n", "header": null, "names": \["text"\], "engine": "python"} | We use `python` engine for `read_csv` in order to handle delimiter of more than 1 character while providing our own column names. |

Please see \(or add\) more at `airbyte-integrations/connectors/source-file/integration_tests/integration_source_test.py` for further usages examples.

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.6   | 2021-08-26 | [5613](https://github.com/airbytehq/airbyte/pull/5613) | Add support to xlsb format |
| 0.2.5   | 2021-07-26 | [4953](https://github.com/airbytehq/airbyte/pull/4953) | Allow non-default port for SFTP type |
| 0.2.4   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.2.3   | 2021-06-01 | [3771](https://github.com/airbytehq/airbyte/pull/3771) | Add Azure Storage Blob Files option |
| 0.2.2   | 2021-04-16 | [2883](https://github.com/airbytehq/airbyte/pull/2883) | Fix CSV discovery memory consumption |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.10  | 2021-02-18 | [2118](https://github.com/airbytehq/airbyte/pull/2118) | Support JSONL format |
| 0.1.9   | 2021-02-02 | [1768](https://github.com/airbytehq/airbyte/pull/1768) | Add test cases for all formats |
| 0.1.8   | 2021-01-27 | [1738](https://github.com/airbytehq/airbyte/pull/1738) | Adopt connector best practices |
| 0.1.7   | 2020-12-16 | [1331](https://github.com/airbytehq/airbyte/pull/1331) | Refactor Python base connector |
| 0.1.6   | 2020-12-08 | [1249](https://github.com/airbytehq/airbyte/pull/1249) | Handle NaN values |
| 0.1.5   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
