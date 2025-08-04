/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumWarmStartState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.sqlserver.Lsn
import io.debezium.connector.sqlserver.SqlServerConnector
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.concurrent.atomic.AtomicLong
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import kotlin.collections.plus
import org.apache.kafka.connect.source.SourceRecord
import org.apache.mina.util.Base64

data class MsSqlServerCdcPosition(val lsn: String) : Comparable<MsSqlServerCdcPosition> {
    override fun compareTo(other: MsSqlServerCdcPosition): Int {
        return lsn.compareTo(other.lsn)
    }
}

@Singleton
class MsSqlServerDebeziumOperations(private val configuration: MsSqlServerSourceConfiguration) :
    CdcPartitionsCreatorDebeziumOperations<MsSqlServerCdcPosition>,
    CdcPartitionReaderDebeziumOperations<MsSqlServerCdcPosition> {

    val recordCounter = AtomicLong(Instant.now().toEpochMilli() * 100_00_000 + 1)

    private val log = KotlinLogging.logger {}

    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull
        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val recordData: JsonNode = if (isDelete) before else after

        // Convert JsonNode to NativeRecordPayload based on stream schema
        val resultRow: NativeRecordPayload = mutableMapOf()

        // Process fields based on stream schema (following MySQL pattern)
        for (field in stream.schema) {
            val fieldValue = recordData[field.id] ?: continue
            when {
                fieldValue.isNull -> {
                    resultRow[field.id] = FieldValueEncoder(null, NullCodec)
                }
                else -> {
                    // Use the field's jsonEncoder if available, otherwise fall back to TextCodec
                    val codec: JsonCodec<*> = field.type.jsonEncoder as? JsonCodec<*> ?: TextCodec
                    @Suppress("UNCHECKED_CAST")
                    resultRow[field.id] =
                        FieldValueEncoder(
                            codec.decode(fieldValue),
                            codec as JsonCodec<Any>,
                        )
                }
            }
        }

        // Set CDC meta-field values
        val transactionMillis: Long = source["ts_ms"].asLong()
        val transactionOffsetDateTime: OffsetDateTime =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(transactionMillis), ZoneOffset.UTC)

        resultRow[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(transactionOffsetDateTime, OffsetDateTimeCodec)
        @Suppress("UNCHECKED_CAST")
        resultRow[CommonMetaField.CDC_DELETED_AT.id] =
            FieldValueEncoder(
                if (isDelete) transactionOffsetDateTime else null,
                (if (isDelete) OffsetDateTimeCodec else NullCodec) as JsonEncoder<Any>
            )

        // Set MSSQL-specific CDC meta-fields
        val commitLsn = source["commit_lsn"].asText()
        resultRow[MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(commitLsn, TextCodec)
        resultRow[MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id] =
            FieldValueEncoder(recordCounter.getAndIncrement(), LongCodec)

        // Return a DeserializedRecord instance.
        return DeserializedRecord(resultRow, changes = emptyMap())
    }

    override fun position(recordValue: DebeziumRecordValue): MsSqlServerCdcPosition? {
        val commitLsn = recordValue.source["commit_lsn"]?.asText()
        return commitLsn?.let { MsSqlServerCdcPosition(it) }
    }

    override fun position(sourceRecord: SourceRecord): MsSqlServerCdcPosition? {
        val commitLsn: String =
            sourceRecord.sourceOffset()[("commit_lsn")]?.toString() ?: return null
        return MsSqlServerCdcPosition(commitLsn)
    }

    override fun position(offset: DebeziumOffset): MsSqlServerCdcPosition {
        if (offset.wrapped.size != 1) {
            throw IllegalArgumentException("Expected exactly 1 key in $offset")
        }
        val offsetValue = offset.wrapped.values.first() as ObjectNode
        val commitLsn = offsetValue["commit_lsn"].asText()
        return MsSqlServerCdcPosition(commitLsn)
    }

    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): JsonNode {
        val stateNode: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        stateNode.set<JsonNode>(MSSQL_CDC_OFFSET, offsetNode)

        val realSchemaHistory: List<HistoryRecord>? = schemaHistory?.wrapped
        if (realSchemaHistory != null) {
            val uncompressedString: String =
                realSchemaHistory.joinToString(separator = "\n") {
                    DocumentWriter.defaultWriter().write(it.document())
                }
            if (uncompressedString.length <= MSSQL_MAX_UNCOMPRESSED_LENGTH) {
                stateNode.put(MSSQL_DB_HISTORY, uncompressedString)
                stateNode.put(MSSQL_IS_COMPRESSED, false)
            } else {
                stateNode.put(MSSQL_IS_COMPRESSED, true)
                val baos = ByteArrayOutputStream()
                val builder = StringBuilder()
                GZIPOutputStream(baos).writer(Charsets.UTF_8).use { it.write(uncompressedString) }

                builder.append("\"")
                builder.append(Base64.encodeBase64(baos.toByteArray()).toString(Charsets.UTF_8))
                builder.append("\"")

                stateNode.put(MSSQL_DB_HISTORY, builder.toString())
            }
        }
        return Jsons.objectNode().apply { set<JsonNode>(MSSQL_STATE, stateNode) }
    }

    override fun deserializeState(opaqueStateValue: JsonNode): DebeziumWarmStartState {
        val stateNode = opaqueStateValue[MSSQL_STATE]
        val offsetNode = stateNode[MSSQL_CDC_OFFSET] as JsonNode
        val offsetMap: Map<JsonNode, JsonNode> =
            offsetNode
                .fields()
                .asSequence()
                .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
                .toMap()
        if (offsetMap.size != 1) {
            throw RuntimeException("Offset object should have 1 key in $opaqueStateValue")
        }
        val offset = DebeziumOffset(offsetMap)

        val historyNode = stateNode[MSSQL_DB_HISTORY]
        val schemaHistory: DebeziumSchemaHistory? =
            historyNode?.let {
                val isCompressed: Boolean = stateNode[MSSQL_IS_COMPRESSED]?.asBoolean() ?: false
                val uncompressedString: String =
                    if (isCompressed) {
                        val textValue: String = it.textValue()
                        val compressedBytes: ByteArray =
                            textValue.substring(1, textValue.length - 1).toByteArray(Charsets.UTF_8)
                        val decoded = Base64.decodeBase64(compressedBytes)

                        GZIPInputStream(ByteArrayInputStream(decoded))
                            .reader(Charsets.UTF_8)
                            .readText()
                    } else {
                        it.textValue()
                    }
                val schemaHistoryList: List<HistoryRecord> =
                    uncompressedString
                        .lines()
                        .filter { it.isNotBlank() }
                        .map { HistoryRecord(DocumentReader.defaultReader().read(it)) }
                DebeziumSchemaHistory(schemaHistoryList)
            }

        return ValidDebeziumWarmStartState(offset, schemaHistory)
    }

    /**
     * Gets the current maximum LSN from SQL Server for CDC cold start. This follows the pattern
     * from the old MSSQL connector and returns the Debezium Lsn type for type safety.
     *
     * @return Lsn object representing the current maximum LSN
     * @throws IllegalStateException if CDC is not enabled or LSN cannot be retrieved
     */
    private fun getCurrentMaxLsn(): Lsn {
        // Create connection using the configuration's JDBC properties
        val url = configuration.jdbcUrlFmt.format(configuration.realHost, configuration.realPort)
        val properties =
            java.util.Properties().apply {
                configuration.jdbcProperties.forEach { (key, value) -> setProperty(key, value) }
            }

        java.sql.DriverManager.getConnection(url, properties).use { connection ->
            connection.createStatement().use { statement ->
                // Query sys.fn_cdc_get_max_lsn() - no need for USE statement since connection is
                // already to the right database
                val query = "SELECT sys.fn_cdc_get_max_lsn() AS max_lsn"
                statement.executeQuery(query).use { resultSet ->
                    if (resultSet.next()) {
                        val lsnBytes = resultSet.getBytes("max_lsn")
                        if (lsnBytes != null && lsnBytes.isNotEmpty()) {
                            // Use Debezium's Lsn class for proper validation and formatting
                            return Lsn.valueOf(lsnBytes)
                        } else {
                            throw IllegalStateException(
                                "CDC is not enabled or no max LSN available for database '${configuration.databaseName}'. " +
                                    "Please ensure: 1) CDC is enabled on the database, 2) At least one table has CDC enabled, " +
                                    "3) The user has necessary permissions to query CDC functions."
                            )
                        }
                    } else {
                        throw IllegalStateException(
                            "Failed to query max LSN from database '${configuration.databaseName}'. " +
                                "The query returned no results."
                        )
                    }
                }
            }
        }
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        val currentLsn = getCurrentMaxLsn()
        val databaseName = configuration.databaseName

        // Create offset structure that matches SQL Server Debezium connector format
        val key =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(
                    Jsons.objectNode().apply {
                        put("server", databaseName)
                        put("database", databaseName)
                    }
                )
            }
        val value =
            Jsons.objectNode().apply {
                put("commit_lsn", currentLsn.toString())
                put("snapshot", true)
                put("snapshot_completed", true)
            }

        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed SQL Server CDC cold start offset with LSN: $currentLsn" }
        return offset
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> {
        return generateCommonDebeziumProperties(streams) + ("snapshot.mode" to "recovery")
    }

    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> {
        return generateCommonDebeziumProperties(streams) + ("snapshot.mode" to "when_needed")
    }

    private fun generateCommonDebeziumProperties(streams: List<Stream>): Map<String, String> {
        val databaseName = configuration.databaseName
        val schemaList = streams.map { it.namespace }.distinct().joinToString(",")
        val messageKeyColumns = buildMessageKeyColumns(streams)

        return DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(SqlServerConnector::class.java)
            .withDebeziumName(databaseName)
            .withHeartbeats(configuration.debeziumHeartbeatInterval)
            .withOffset()
            .withSchemaHistory()
            .withStreams(streams)
            .with("include.schema.changes", "false")
            .with("provide.transaction.metadata", "false")
            .with("snapshot.isolation.mode", "read_committed")
            .with("schema.include.list", schemaList)
            .let { builder ->
                if (messageKeyColumns.isNotEmpty()) {
                    builder.with("message.key.columns", messageKeyColumns)
                } else {
                    builder
                }
            }
            .withDatabase("hostname", configuration.realHost)
            .withDatabase("port", configuration.realPort.toString())
            .withDatabase("user", configuration.jdbcProperties["user"].toString())
            .withDatabase("password", configuration.jdbcProperties["password"].toString())
            .withDatabase("dbname", databaseName)
            .withDatabase("names", databaseName)
            .with("database.encrypt", configuration.jdbcProperties["encrypt"] ?: "false")
            .with(
                "driver.trustServerCertificate",
                configuration.jdbcProperties["trustServerCertificate"] ?: "true"
            )
            // Register the MSSQL custom converter
            .with("converters", "mssql_converter")
            .with("mssql_converter.type", MsSqlServerDebeziumConverter::class.java.name)
            .with("binary.handling.mode", "base64")
            .with("snapshot.locking.mode", "none")
            // Set poll.interval.ms to control how often Debezium queries for new data
            // This value is now configurable and validated to be smaller than heartbeat.interval.ms
            .with(
                "poll.interval.ms",
                (configuration.incrementalReplicationConfiguration as CdcIncrementalConfiguration)
                    .pollIntervalMs
                    .toString()
            )
            // Enable heartbeat timeout for MSSQL to detect idle database states
            .with("airbyte.first.record.wait.seconds", "60")
            .buildMap()
    }

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        return value.source["table"]?.asText()
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        return value.source["schema"]?.asText()
    }

    /**
     * Builds the message.key.columns property value for Debezium. Format:
     * "schema1.table1:keyCol1,keyCol2;schema2.table2:keyCol1,keyCol2" This replicates the logic
     * from the old MSSQL connector's getMessageKeyColumnValue method.
     */
    private fun buildMessageKeyColumns(streams: List<Stream>): String {
        return streams
            .filter { it.configuredPrimaryKey?.isNotEmpty() == true }
            .joinToString(";") { stream ->
                val tableId =
                    "${escapeSpecialChars(stream.namespace)}.${escapeSpecialChars(stream.name)}"
                val keyCols =
                    stream.configuredPrimaryKey!!.joinToString(",") { escapeSpecialChars(it.id) }
                "$tableId:$keyCols"
            }
    }

    /**
     * Escapes special characters for Debezium message key columns. Escapes: comma (,), period (.),
     * semicolon (;), and colon (:) This replicates the logic from the old MSSQL connector's
     * escapeSpecialChars method.
     */
    private fun escapeSpecialChars(input: String?): String {
        if (input == null) return ""
        return input
            .map { char ->
                when (char) {
                    ',',
                    '.',
                    ';',
                    ':' -> "\\${char}"
                    else -> char.toString()
                }
            }
            .joinToString("")
    }

    companion object {
        const val MSSQL_MAX_UNCOMPRESSED_LENGTH = 1024 * 1024
        const val MSSQL_STATE = "state"
        const val MSSQL_CDC_OFFSET = "mssql_cdc_offset"
        const val MSSQL_DB_HISTORY = "mssql_db_history"
        const val MSSQL_IS_COMPRESSED = "is_compressed"
    }
}
