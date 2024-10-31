## Behavior

The Airbyte protocol defines the actions `spec`, `discover`, `check` and `read` for a source to be compliant. Here is the high-level description of the flow for a file-based source:

- spec: calls AbstractFileBasedSpec.documentation_url and AbstractFileBasedSpec.schema to return a ConnectorSpecification.
- discover: calls Source.streams, and subsequently Stream.get_json_schema; this uses Source.open_file to open files during schema discovery.
- check: Source.check_connection is called from the entrypoint code (in the main CDK).
- read: Stream.read_records calls Stream.list_files which calls Source.list_matching_files, and then also uses Source.open_file to parse records from the file handle.

## How to Implement Your Own

To create a file-based source a user must extend three classes – AbstractFileBasedSource, AbstractFileBasedSpec, and AbstractStreamReader – to create an implementation for the connector’s specific storage system. They then initialize a FileBasedSource with the instance of AbstractStreamReader specific to their storage system.

The abstract classes house the vast majority of the logic required by file-based sources. For example, when extending AbstractStreamReader, users only have to implement three methods:

- list_matching_files: lists files matching the glob pattern(s) provided in the config.
- open_file: returns a file handle for reading.
- config property setter: concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct config type for that type of StreamReader.

The result is that an implementation of a source might look like this:

```
class CustomStreamReader(AbstractStreamReader):
    def open_file(self, remote_file: RemoteFile) -> FileHandler:
        <...>

    def get_matching_files(
        self,
        globs: List[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        <...>

    @config.setter
    def config(self, value: Config):
        assert isinstance(value, CustomConfig)
        self._config = value


class CustomConfig(AbstractFileBasedSpec):
    @classmethod
    def documentation_url(cls) -> AnyUrl:
        return AnyUrl("https://docs.airbyte.com/integrations/sources/s3", scheme="https")

    a_spec_field: str = Field(title="A Spec Field", description="This is where you describe the fields of the spec", order=0)
    <...>
```

For more information, feel free to check the docstrings of each classes or check specific implementations (like source-s3).

## Supported File Types

### Avro

Avro is a serialization format developed by [Apache](https://avro.apache.org/docs/). Avro configuration options for the file-based CDK:

- `double_as_string`: Whether to convert double fields to strings. This is recommended if you have decimal numbers with a high degree of precision because there can be a loss precision when handling floating point numbers.

### CSV

CSV is a format loosely described by [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180). The format is quite flexible which leads to a ton of options to consider:

- `delimiter`: The character delimiting individual cells in the CSV data. By name, CSV is comma separated so the default value is `,`
- `quote_char`: When quoted fields are used, it is possible for a field to span multiple lines, even when line breaks appear within such field. The default quote character is `"`.
- `escape_char`: The character used for escaping special characters.
- `encoding`: The character encoding of the file. By default, `UTF-8`
- `double_quote`: Whether two quotes in a quoted CSV value denote a single quote in the data.
- `quoting_behavior`: The quoting behavior determines when a value in a row should have quote marks added around it.
- `skip_rows_before_header`: The number of rows to skip before the header row. For example, if the header row is on the 3rd row, enter 2 in this field.
- `skip_rows_after_header`: The number of rows to skip after the header row.
- `autogenerate_column_names`: If your CSV does not have a header row, the file-based CDK will need this enable to generate column names.
- `null_values`: As CSV does not explicitly define a value for null values, the user can specify a set of case-sensitive strings that should be interpreted as null values.
- `true_values`: As CSV does not explicitly define a value for positive boolean, the user can specify a set of case-sensitive strings that should be interpreted as true values.
- `false_values`: As CSV does not explicitly define a value for negative boolean, the user can specify a set of case-sensitive strings that should be interpreted as false values.

### JSONL

[JSONL](https://jsonlines.org/) (or JSON Lines) is a format where each row is a JSON object. There are no configuration option for this format. For backward compatibility reasons, the JSONL parser currently supports multiline objects even though this is not part of the JSONL standard. Following some data gathering, we reserve the right to remove the support for this. Given that files have multiline JSON objects, performances will be slow.

### Parquet

Parquet is a file format defined by [Apache](https://parquet.apache.org/). Configuration options are:

- `decimal_as_float`: Whether to convert decimal fields to floats. There is a loss of precision when converting decimals to floats, so this is not recommended.

### Document file types (PDF, DOCX, Markdown)

For file share source connectors, the `unstructured` parser can be used to parse document file types. The textual content of the whole file will be parsed as a single record with a `content` field containing the text encoded as markdown.

To use the unstructured parser, the libraries `poppler` and `tesseract` need to be installed on the system running the connector. For example, on Ubuntu, you can install them with the following command:

```
apt-get install -y tesseract-ocr poppler-utils
```

on Mac, you can install these via brew:

```
brew install poppler
brew install tesseract
```

## Schema

Having a schema allows for the file-based CDK to take action when there is a discrepancy between a record and what are the expected types of the record fields.

Schema can be either inferred or user provided.

- If the user defines it a format using JSON types, inference will not apply. Input schemas are a key/value pair of strings describing column name and data type. Supported types are `["string", "number", "integer", "object", "array", "boolean", "null"]`. For example, `{"col1": "string", "col2": "boolean"}`.
- If the user enables schemaless sync, schema will `{"data": "object"}` and therefore emitted records will look like `{"data": {"col1": val1, …}}`. This is recommended if the contents between files in the stream vary significantly, and/or if data is very nested.
- Else, the file-based CDK will infer the schema depending on the file type. Some file formats defined the schema as part of their metadata (like Parquet), some do on the record-level (like Avro) and some don't have any explicit typing (like JSON or CSV). Note that all CSV values are inferred as strings except where we are supporting legacy configurations. Any file format that does not define their schema on a metadata level will require the file-based CDK to iterate to a number of records. There is a limit of bytes that will be consumed in order to infer the schema.

### Validation Policies

Users will be required to select one of 3 different options, in the event that records are encountered that don’t conform to the schema.

- Skip nonconforming records: check each record to see if it conforms to the user-input or inferred schema; skip the record if it doesn't conform. We keep a count of the number of records in each file that do and do not conform and emit a log message with these counts once we’re done reading the file.
- Emit all records: emit all records, even if they do not conform to the user-provided or inferred schema. Columns that don't exist in the configured catalog probably won't be available in the destination's table since that's the current behavior.
  Only error if there are conflicting field types or malformed rows.
- Stop the sync and wait for schema re-discovery: if a record is encountered that does not conform to the configured catalog’s schema, we log a message and stop the whole sync. Note: this option is not recommended if the files have very different columns or datatypes, because the inferred schema may vary significantly at discover time.

When the `schemaless` is enabled, validation will be skipped.

## Breaking Changes (compared to previous S3 implementation)

- [CSV] Mapping of type `array` and `object`: before, they were mapped as `large_string` and hence casted as strings. Given the new changes, if `array` or `object` is specified, the value will be casted as `array` and `object` respectively.
- [CSV] Before, a string value would not be considered as `null_values` if the column type was a string. We will now start to cast string columns with values matching `null_values` to null.
- [CSV] `decimal_point` option is deprecated: It is not possible anymore to use another character than `.` to separate the integer part from non-integer part. Given that the float is format with another character than this, it will be considered as a string.
- [Parquet] `columns` option is deprecated: You can use Airbyte column selection in order to have the same behavior. We don't expect it, but this could have impact on the performance as payload could be bigger.

## Incremental syncs

The file-based connectors supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                                        | Supported? |
| :--------------------------------------------- | :--------- |
| Full Refresh Sync                              | Yes        |
| Incremental Sync                               | Yes        |
| Replicate Incremental Deletes                  | No         |
| Replicate Multiple Files \(pattern matching\)  | Yes        |
| Replicate Multiple Streams \(distinct tables\) | Yes        |
| Namespaces                                     | No         |

We recommend you do not manually modify files that are already synced. The connector has file-level granularity, which means adding or modifying a row in a CSV file will trigger a re-sync of the content of that file.

### Incremental sync

After the initial sync, the connector only pulls files that were modified since the last sync.

The connector checkpoints the connection states when it is done syncing all files for a given timestamp. The connection's state only keeps track of the last 10 000 files synced. If more than 10 000 files are synced, the connector won't be able to rely on the connection state to deduplicate files. In this case, the connector will initialize its cursor to the minimum between the earliest file in the history, or 3 days ago.

Both the maximum number of files, and the time buffer can be configured by connector developers.
