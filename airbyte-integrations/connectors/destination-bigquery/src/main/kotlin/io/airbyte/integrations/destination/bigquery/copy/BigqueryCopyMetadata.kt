/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.google.cloud.bigquery.Field
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.csv.toCsvHeader
import io.airbyte.cdk.load.data.json.AirbyteTypeToJsonSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.security.MessageDigest
import java.util.UUID

/** Metadata for completed load inputs, independent of temporary execution tables and GCS keys. */
class BigqueryCopyMetadata(
    private val config: S3CopyConfiguration,
    private val bigqueryConfiguration: BigqueryConfiguration,
    private val names: TableCatalogByDescriptor,
    private val runId: UUID,
    private val dataChannelFormat: DataChannelFormat,
    private val configuredCatalog: ConfiguredAirbyteCatalog? = null,
) {
    private val mapper = ObjectMapper()
    private val raw = bigqueryConfiguration.legacyRawTablesOnly
    private val gcs = bigqueryConfiguration.loadingMethod is GcsStagingConfiguration
    private val formatVersion = if (gcs) FORMAT_VERSION else STANDARD_INSERT_FORMAT_VERSION

    fun descriptor(stream: DestinationStream): Map<String, Any?> {
        validateGeneration(stream)
        val tableInfo =
            requireNotNull(names[stream.mappedDescriptor]) {
                "Missing BigQuery table mapping for ${stream.mappedDescriptor}"
            }
        val table =
            requireNotNull(
                if (raw) tableInfo.tableNames.rawTableName else tableInfo.tableNames.finalTableName
            ) { "Missing logical BigQuery table for ${stream.mappedDescriptor}" }
        // Use the same schemas as the loader factories. Standard raw inserts include loaded-at
        // in their target schema, even though neither standard formatter writes that field.
        val headers =
            if (gcs) stream.schema.withAirbyteMeta(!raw).toCsvHeader().toList() else emptyList()
        val fields =
            if (raw)
                (if (gcs) BigQueryRecordFormatter.CSV_SCHEMA else BigQueryRecordFormatter.SCHEMA_V2)
                    .fields
                    .toList()
            else
                BigQueryRecordFormatter.getDirectLoadSchema(stream, tableInfo.columnNameMapping)
                    .fields
                    .toList()
        check(!gcs || headers.size == fields.size) {
            "BigQuery CSV header and load schema disagree"
        }
        val columns =
            fields.mapIndexed { ordinal, field ->
                val sourcePath =
                    if (raw || ordinal < AIRBYTE_COLUMN_COUNT) emptyList<String>()
                    else if (gcs) listOf(headers[ordinal])
                    else
                        listOf(
                            stream.schema.asColumns().keys.elementAt(ordinal - AIRBYTE_COLUMN_COUNT)
                        )
                fieldDescriptor(field) +
                    if (gcs)
                        mapOf(
                            "csv_ordinal" to ordinal,
                            "csv_header" to headers[ordinal],
                            "source_path" to sourcePath,
                        )
                    else
                        mapOf(
                            "source_path" to sourcePath,
                            "json_field" to
                                field.name.takeUnless {
                                    raw && it == Meta.COLUMN_NAME_AB_LOADED_AT
                                },
                            "presence" to
                                when {
                                    raw && field.name == Meta.COLUMN_NAME_AB_LOADED_AT ->
                                        "omitted; loads as SQL NULL"
                                    sourcePath.isNotEmpty() &&
                                        dataChannelFormat != DataChannelFormat.PROTOBUF ->
                                        "omitted when missing, null, or nulled by validation"
                                    else -> "always emitted"
                                },
                        )
            }

        fun pathMapping(path: List<String>): Map<String, Any?> {
            require(path.isNotEmpty()) { "Configured BigQuery key paths must not be empty" }
            val header = if (raw) Meta.COLUMN_NAME_DATA else path.first()
            val ordinal = if (gcs) headers.indexOf(header) else -1
            val target =
                if (gcs) {
                    require(ordinal >= 0) {
                        "Configured key/cursor field $header is absent from the CSV"
                    }
                    fields[ordinal].name
                } else {
                    val mapped =
                        if (raw) Meta.COLUMN_NAME_DATA else tableInfo.columnNameMapping[header]
                    requireNotNull(mapped?.takeIf { name -> fields.any { it.name == name } }) {
                        "Configured key/cursor field $header is absent from the standard insert schema"
                    }
                }
            val withinColumn = if (raw) path else path.drop(1)
            return mapOf("source_path" to path) +
                (if (gcs) mapOf("csv_ordinal" to ordinal, "csv_header" to header)
                else mapOf("json_field" to target)) +
                mapOf(
                    "target_column" to target,
                    "path_within_column" to withinColumn,
                    "target_path" to (listOf(target) + withinColumn),
                )
        }

        // Append/overwrite DestinationStreams do not retain configured keys or cursors.
        val configured =
            configuredCatalog?.streams?.singleOrNull {
                it.stream.namespace == stream.unmappedNamespace &&
                    it.stream.name == stream.unmappedName
            }
                ?: stream.asProtocolObject()
        val primaryKey = configured.primaryKey.orEmpty()
        val cursor = configured.cursorField.orEmpty()
        val layout =
            mapOf(
                "format_version" to formatVersion,
                "loading_strategy" to
                    when (bigqueryConfiguration.loadingMethod) {
                        is GcsStagingConfiguration -> "GCS_STAGING"
                        BatchedStandardInsertConfiguration -> "BATCHED_STANDARD_INSERT"
                    },
                "table_mode" to if (raw) "raw" else "direct",
                "input_format" to dataChannelFormat.name,
                (if (gcs) "csv" to csvDescriptor() else "ndjson" to ndjsonDescriptor()),
                "columns" to columns,
                "source_schema" to AirbyteTypeToJsonSchema().convert(stream.schema),
                "import_type" to configured.destinationSyncMode.name,
                "primary_key" to primaryKey,
                "primary_key_mapping" to primaryKey.map(::pathMapping),
                "cursor" to cursor,
                "cursor_mapping" to
                    if (cursor.isEmpty()) emptyList() else listOf(pathMapping(cursor)),
                "deduplication_cursor" to
                    if (stream.importType is Dedupe) {
                        mapOf(
                            "configured" to cursor.isNotEmpty(),
                            "target_column" to
                                if (cursor.isEmpty()) Meta.COLUMN_NAME_AB_EXTRACTED_AT
                                else if (raw) Meta.COLUMN_NAME_DATA
                                else tableInfo.columnNameMapping[cursor.first()],
                            "path_within_column" to if (raw) cursor else cursor.drop(1),
                            "performed_in_raw_mode" to false,
                            "extracted_at_tiebreaker" to true,
                        )
                    } else null,
                "cdc" to
                    mapOf(
                        "deleted_at_field_present" to
                            stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN),
                        "deleted_at_source_path" to listOf(CDC_DELETED_AT_COLUMN),
                        "deletion_mode" to bigqueryConfiguration.cdcDeletionMode.name,
                        "archive_deletes_rows" to false,
                    ),
                "load_options" to
                    if (gcs)
                        mapOf(
                            "format" to "CSV",
                            "skipLeadingRows" to 1,
                            "allowQuotedNewLines" to true,
                            "allowJaggedRows" to true,
                            "preserveAsciiControlCharacters" to true,
                            "nullMarker" to BigQueryConsts.NULL_MARKER,
                            "writeDisposition" to "WRITE_APPEND",
                            "unspecified_options" to "inherited BigQuery server defaults",
                        )
                    else
                        mapOf(
                            "format" to "NEWLINE_DELIMITED_JSON",
                            "createDisposition" to "CREATE_IF_NEEDED",
                            "unspecified_options" to "inherited BigQuery server defaults",
                        ),
            )
        val result =
            identity(stream) +
                mapOf(
                    "format_version" to formatVersion,
                    "connector_version" to
                        (System.getenv("AIRBYTE_CONNECTOR_VERSION")
                            ?: javaClass.`package`.implementationVersion),
                    "logical_table" to
                        mapOf(
                            "project" to bigqueryConfiguration.projectId,
                            "dataset" to table.namespace,
                            "table" to table.name,
                        ),
                    "layout" to layout,
                    "scope" to "load inputs; not final table publication or a final table snapshot",
                    "loaded_record_count_meaning" to "BigQuery load job outputRows",
                ) +
                if (gcs) emptyMap()
                else
                    mapOf(
                        "input_record_count_meaning" to
                            "Successful formatter-byte appends to the standard insert archive batch"
                    )
        return result + ("schema_id" to schemaId(result))
    }

    /** SHA-256 of canonical layout JSON: object keys sorted recursively, array order preserved. */
    fun schemaId(descriptor: Map<String, Any?>): String =
        hash(requireNotNull(descriptor["layout"]) { "Schema descriptor has no layout" })

    /** Use this for archive JSON as well as hashing so null fields survive serialization. */
    fun serialize(value: Any): ByteArray = mapper.writeValueAsBytes(value)

    /** The identity matches the name-only routing contract, and stays stable across runs. */
    fun streamKey(stream: DestinationStream): String =
        hash(
                listOf(
                    config.workspaceId.toString(),
                    config.sourceId.toString(),
                    config.connectionId.toString(),
                    stream.unmappedName,
                )
            )
            .take(32)

    fun runPath(stream: DestinationStream): String =
        "${config.prefix}/workspaces/${config.workspaceId}/sources/${config.sourceId}/connections/${config.connectionId}/streams/${escape(stream.unmappedName)}/runs/$runId"

    /** Call once per stream/run when minimumGenerationId is positive; retain on later failures. */
    fun cutoff(stream: DestinationStream): Map<String, Any?> {
        validateGeneration(stream)
        require(stream.minimumGenerationId > 0) {
            "No cutoff requested for minimum generation zero"
        }
        return identity(stream) +
            mapOf(
                "format_version" to formatVersion,
                "event_type" to "generation_cutoff_requested",
                "event_id" to UUID.randomUUID().toString(),
                "discard" to
                    mapOf(
                        "field" to Meta.COLUMN_NAME_AB_GENERATION_ID,
                        "comparison" to "strictly_less_than",
                        "value" to stream.minimumGenerationId,
                    ),
            )
    }

    private fun identity(stream: DestinationStream): Map<String, Any?> =
        mapOf(
            "workspace_id" to config.workspaceId.toString(),
            "source_id" to config.sourceId.toString(),
            "connection_id" to config.connectionId.toString(),
            "stream_key" to streamKey(stream),
            "original_stream" to
                mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName),
            "mapped_stream" to
                mapOf(
                    "namespace" to stream.mappedDescriptor.namespace,
                    "name" to stream.mappedDescriptor.name,
                ),
            "run_id" to runId.toString(),
            "sync_id" to stream.syncId,
            "generation_id" to stream.generationId,
            "minimum_generation_id" to stream.minimumGenerationId,
        )

    private fun csvDescriptor(): Map<String, Any?> =
        mapOf(
            "encoding" to "UTF-8",
            "compression" to "gzip",
            "header_rows" to 1,
            "ordinal_base" to 0,
            "delimiter" to ",",
            "quote" to "\"",
            "quote_mode" to "NON_NUMERIC",
            "escape" to "double the quote character; backslashes are literal",
            "record_separator" to "\r\n",
            "null_representation" to
                if (raw) "JSON null inside _airbyte_data" else BigQueryConsts.NULL_MARKER,
            "conversions" to
                if (raw) {
                    listOf(
                        "_airbyte_data and _airbyte_meta are serialized JSON stored in STRING columns",
                        "_airbyte_extracted_at is an ISO-8601 UTC timestamp from emitted-at milliseconds",
                        if (dataChannelFormat == DataChannelFormat.PROTOBUF)
                            "Payload is reconstructed from declared fields in proxy order; missing values become JSON null and undeclared fields are unavailable"
                        else
                            "Payload preserves source JSON fields, including undeclared fields and JSON null",
                    )
                } else {
                    listOf(
                        "Missing, null, and nulled invalid fields share the quoted \\N marker; literal \\N strings are indistinguishable",
                        "Empty strings are quoted empty fields, distinct from the null marker",
                        "Objects, arrays and non-legacy unions are serialized JSON; legacy unions use their selected type",
                        "Date/time values are normalized by BigQuery formatters; timezone-bearing TIME is stored as STRING",
                        "INT64 overflow becomes null; NUMERIC is bounded to precision 38 and rounded HALF_UP to scale 9",
                        if (dataChannelFormat == DataChannelFormat.PROTOBUF)
                            "Extracted-at uses BigQuery timestamp text; generation ID is a quoted string"
                        else
                            "Extracted-at uses ISO-8601 UTC timestamp text; generation ID is an unquoted number",
                    )
                },
        )

    private fun ndjsonDescriptor(): Map<String, Any?> =
        mapOf(
            "encoding" to "UTF-8",
            "compression" to "none",
            "content_type" to "application/x-ndjson",
            "batch_path" to "batches/<uuid>.jsonl",
            "record_separator" to System.lineSeparator(),
            "trailing_record_separator" to true,
            "null_representation" to
                when {
                    raw && dataChannelFormat != DataChannelFormat.PROTOBUF ->
                        "Source JSON null and absent fields are preserved inside the serialized _airbyte_data string"
                    raw ->
                        "Missing, null, and nulled invalid declared fields become JSON null inside the serialized _airbyte_data string"
                    dataChannelFormat == DataChannelFormat.PROTOBUF ->
                        "Missing, null, and nulled invalid declared fields are emitted as JSON null"
                    else -> "Missing, null, and nulled invalid declared fields are omitted"
                },
            "conversions" to
                listOfNotNull(
                    "Empty strings and literal \\N strings are preserved; there is no CSV null marker",
                    "_airbyte_extracted_at uses BigQuery timestamp text from emitted-at milliseconds; generation ID is a JSON number",
                    if (raw)
                        "_airbyte_data and _airbyte_meta are JSON strings containing serialized JSON; _airbyte_loaded_at is omitted and loads as SQL NULL"
                    else
                        "_airbyte_meta is a JSON object; user fields use mapped target names and objects/arrays are JSON values",
                    if (raw && dataChannelFormat != DataChannelFormat.PROTOBUF)
                        "Payload preserves source JSON fields, including undeclared fields, without destination validation; metadata preserves source changes and adds sync_id"
                    else
                        "Declared fields are formatted and validated; undeclared top-level fields are unavailable in the output; validation changes are included in _airbyte_meta",
                    if (dataChannelFormat == DataChannelFormat.PROTOBUF)
                        "Payload is reconstructed from declared fields in proxy order"
                    else null,
                    if (!raw || dataChannelFormat == DataChannelFormat.PROTOBUF)
                        "Legacy unions use their selected type; date/time values are normalized by BigQuery formatters; timezone-bearing TIME is stored as STRING"
                    else null,
                    if (!raw || dataChannelFormat == DataChannelFormat.PROTOBUF)
                        "INT64 overflow becomes null; NUMERIC is bounded to precision 38 and rounded HALF_UP to scale 9"
                    else null,
                ),
        )

    private fun fieldDescriptor(field: Field): Map<String, Any?> =
        mapOf(
            "target_field" to field.name,
            "type" to field.type.standardType.name,
            "mode" to (field.mode ?: Field.Mode.NULLABLE).name,
            "nullable" to ((field.mode ?: Field.Mode.NULLABLE) == Field.Mode.NULLABLE),
            "fields" to field.subFields?.map(::fieldDescriptor).orEmpty(),
        )

    private fun validateGeneration(stream: DestinationStream) {
        require(
            stream.generationId >= 0 &&
                (stream.minimumGenerationId == 0L ||
                    stream.minimumGenerationId == stream.generationId)
        ) { "BigQuery S3 copy supports minimum generation zero or equal to current generation" }
    }

    private fun hash(value: Any): String {
        val bytes = mapper.writeValueAsBytes(canonical(mapper.valueToTree(value)))
        return MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") {
            "%02x".format(it.toInt() and 0xff)
        }
    }

    private fun canonical(node: JsonNode): JsonNode =
        when {
            node.isObject ->
                mapper.createObjectNode().also { result ->
                    node.fieldNames().asSequence().sorted().forEach { key ->
                        result.set<JsonNode>(key, canonical(node[key]))
                    }
                }
            node.isArray ->
                mapper.createArrayNode().also { result ->
                    node.forEach { result.add(canonical(it)) }
                }
            else -> node
        }

    private fun escape(name: String): String {
        require(name.isNotEmpty()) { "Archive stream name must not be empty" }
        return name.toByteArray(Charsets.UTF_8).joinToString("") { byte ->
            val value = byte.toInt() and 0xff
            val char = value.toChar()
            if (
                char in 'a'..'z' ||
                    char in 'A'..'Z' ||
                    char in '0'..'9' ||
                    char in "-_~" ||
                    (char == '.' && name != "." && name != "..")
            )
                char.toString()
            else "%%%02X".format(value)
        }
    }

    companion object {
        const val FORMAT_VERSION = "bigquery-gcs-load-csv-gzip-v1"
        const val STANDARD_INSERT_FORMAT_VERSION = "bigquery-load-ndjson-v1"
        private const val AIRBYTE_COLUMN_COUNT = 4
    }
}
