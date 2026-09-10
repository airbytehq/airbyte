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

    fun descriptor(stream: DestinationStream): Map<String, Any?> {
        require(bigqueryConfiguration.loadingMethod is GcsStagingConfiguration) {
            "BigQuery S3 copy metadata only supports GCS staging"
        }
        validateGeneration(stream)
        val tableInfo =
            requireNotNull(names[stream.mappedDescriptor]) {
                "Missing BigQuery table mapping for ${stream.mappedDescriptor}"
            }
        val table =
            requireNotNull(
                if (raw) tableInfo.tableNames.rawTableName else tableInfo.tableNames.finalTableName
            ) {
                "Missing logical BigQuery table for ${stream.mappedDescriptor}"
            }
        // These are the same helpers used by both formatting writers and the bulk loader factory.
        val headers = stream.schema.withAirbyteMeta(!raw).toCsvHeader().toList()
        val fields =
            if (raw) BigQueryRecordFormatter.CSV_SCHEMA.fields.toList()
            else
                BigQueryRecordFormatter.getDirectLoadSchema(stream, tableInfo.columnNameMapping)
                    .fields
                    .toList()
        check(headers.size == fields.size) { "BigQuery CSV header and load schema disagree" }
        val columns =
            headers.mapIndexed { ordinal, header ->
                fieldDescriptor(fields[ordinal]) +
                    mapOf(
                        "csv_ordinal" to ordinal,
                        "csv_header" to header,
                        "source_path" to
                            if (raw || ordinal < AIRBYTE_COLUMN_COUNT) emptyList<String>()
                            else listOf(header),
                    )
            }

        fun pathMapping(path: List<String>): Map<String, Any?> {
            require(path.isNotEmpty()) { "Configured BigQuery key paths must not be empty" }
            val header = if (raw) Meta.COLUMN_NAME_DATA else path.first()
            val ordinal = headers.indexOf(header)
            require(ordinal >= 0) { "Configured key/cursor field $header is absent from the CSV" }
            val target = fields[ordinal].name
            val withinColumn = if (raw) path else path.drop(1)
            return mapOf(
                "source_path" to path,
                "csv_ordinal" to ordinal,
                "csv_header" to header,
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
            } ?: stream.asProtocolObject()
        val primaryKey = configured.primaryKey.orEmpty()
        val cursor = configured.cursorField.orEmpty()
        val layout =
            mapOf(
                "format_version" to FORMAT_VERSION,
                "loading_strategy" to "GCS_STAGING",
                "table_mode" to if (raw) "raw" else "direct",
                "input_format" to dataChannelFormat.name,
                "csv" to csvDescriptor(),
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
                    mapOf(
                        "format" to "CSV",
                        "skipLeadingRows" to 1,
                        "allowQuotedNewLines" to true,
                        "allowJaggedRows" to true,
                        "preserveAsciiControlCharacters" to true,
                        "nullMarker" to BigQueryConsts.NULL_MARKER,
                        "writeDisposition" to "WRITE_APPEND",
                        "unspecified_options" to "inherited BigQuery server defaults",
                    ),
            )
        val result =
            identity(stream) +
                mapOf(
                    "format_version" to FORMAT_VERSION,
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
                "format_version" to FORMAT_VERSION,
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
        ) {
            "BigQuery S3 copy supports minimum generation zero or equal to current generation"
        }
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
        private const val AIRBYTE_COLUMN_COUNT = 4
    }
}
