/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder.Companion.AIRBYTE_HEARTBEAT_TIMEOUT_SECONDS
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumWarmStartState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.read.cdc.InvalidDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ResetDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.ssh.TunnelSession
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
import java.sql.Connection
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
class MsSqlServerDebeziumOperations(
    private val jdbcConnectionFactory: JdbcConnectionFactory,
    private val configuration: MsSqlServerSourceConfiguration
) :
    CdcPartitionsCreatorDebeziumOperations<MsSqlServerCdcPosition>,
    CdcPartitionReaderDebeziumOperations<MsSqlServerCdcPosition> {

    // Generates globally unique cursor values for CDC records by combining
    // current timestamp with an incrementing counter. This ensures monotonically
    // increasing values across sync restarts and avoids collisions.
    val cdcCursorGenerator = AtomicLong(Instant.now().toEpochMilli() * 10_000_000 + 1)

    private val log = KotlinLogging.logger {}

    @Suppress("UNCHECKED_CAST")
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

                    // Handle numeric and binary values from Debezium (can come as JSON strings or
                    // numbers)
                    val decodedValue =
                        when {
                            // BigDecimal: handle both string and number
                            fieldValue.isTextual && codec is BigDecimalCodec ->
                                java.math.BigDecimal(fieldValue.asText())
                            fieldValue.isNumber && codec is BigDecimalCodec ->
                                fieldValue.decimalValue()

                            // Int: handle both string and number
                            fieldValue.isTextual && codec is IntCodec -> fieldValue.asText().toInt()
                            fieldValue.isNumber && codec is IntCodec -> fieldValue.intValue()

                            // Long: handle both string and number
                            fieldValue.isTextual && codec is LongCodec ->
                                fieldValue.asText().toLong()
                            fieldValue.isNumber && codec is LongCodec -> fieldValue.longValue()

                            // Float: handle both string and number
                            fieldValue.isTextual && codec is FloatCodec ->
                                fieldValue.asText().toFloat()
                            fieldValue.isNumber && codec is FloatCodec -> fieldValue.floatValue()

                            // Double: handle both string and number
                            fieldValue.isTextual && codec is DoubleCodec ->
                                fieldValue.asText().toDouble()
                            fieldValue.isNumber && codec is DoubleCodec -> fieldValue.doubleValue()

                            // Binary: handle base64 string
                            fieldValue.isTextual && codec is BinaryCodec ->
                                java.nio.ByteBuffer.wrap(
                                    java.util.Base64.getDecoder().decode(fieldValue.asText())
                                )
                            else -> codec.decode(fieldValue)
                        }

                    resultRow[field.id] = FieldValueEncoder(decodedValue, codec as JsonCodec<Any>)
                }
            }
        }

        // Set CDC meta-field values
        val transactionMillis: Long = source["ts_ms"].asLong()
        val transactionOffsetDateTime: OffsetDateTime =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(transactionMillis), ZoneOffset.UTC)

        resultRow[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(
                transactionOffsetDateTime,
                CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder as JsonEncoder<Any>
            )

        resultRow[CommonMetaField.CDC_DELETED_AT.id] =
            FieldValueEncoder(
                if (isDelete) transactionOffsetDateTime else null,
                (if (isDelete) CommonMetaField.CDC_DELETED_AT.type.jsonEncoder else NullCodec)
                    as JsonEncoder<Any>
            )

        // Set MSSQL-specific CDC meta-fields
        val commitLsn = source["commit_lsn"].asText()
        resultRow[MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                commitLsn,
                MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_LSN.type.jsonEncoder
                    as JsonEncoder<Any>
            )
        resultRow[MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id] =
            FieldValueEncoder(
                cdcCursorGenerator.getAndIncrement(),
                MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.type.jsonEncoder
                    as JsonEncoder<Any>
            )

        val eventSerialNo = source["event_serial_no"]?.asInt()?.let { "$it" } ?: "0"
        resultRow[MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO.id] =
            FieldValueEncoder(
                eventSerialNo,
                MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_EVENT_SERIAL_NO.type.jsonEncoder
                    as JsonEncoder<Any>
            )

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
        // Sanitize offset before saving to state to fix heartbeat corruption
        val sanitizedOffset = sanitizeOffset(offset)

        val stateNode: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in sanitizedOffset.wrapped) {
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
                .fieldNames()
                .asSequence()
                .map { k -> Jsons.readTree(k) to Jsons.readTree(offsetNode[k].textValue()) }
                .toMap()

        // Handle legacy state with multiple offset keys (e.g., different database name casings)
        val finalOffsetMap =
            when {
                offsetMap.size == 1 -> offsetMap
                offsetMap.size > 1 -> {
                    log.warn {
                        "Found ${offsetMap.size} offset keys in saved state. This may be from a legacy connector version. " +
                            "Selecting the offset with the highest LSN (most recent position)."
                    }

                    // Select the offset with the highest LSN
                    val selectedEntry =
                        offsetMap.entries.maxByOrNull { (_, value) ->
                            val offsetValue = value as ObjectNode
                            val commitLsn = offsetValue["commit_lsn"]?.asText()
                            try {
                                commitLsn?.let { Lsn.valueOf(it) } ?: Lsn.NULL
                            } catch (e: Exception) {
                                log.warn(e) { "Failed to parse LSN from offset value: $value" }
                                Lsn.NULL
                            }
                        }

                    if (selectedEntry == null) {
                        throw RuntimeException(
                            "Unable to select valid offset from multiple keys in $opaqueStateValue"
                        )
                    }

                    log.info {
                        "Selected offset key with commit_lsn='${(selectedEntry.value as ObjectNode)["commit_lsn"]?.asText()}' " +
                            "from ${offsetMap.size} available offset keys."
                    }

                    mapOf(selectedEntry.key to selectedEntry.value)
                }
                else ->
                    throw RuntimeException(
                        "Offset object must have at least 1 key in $opaqueStateValue"
                    )
            }

        val offset = DebeziumOffset(finalOffsetMap)

        // Check if the saved LSN is valid
        val savedLsn =
            try {
                val offsetValue = offset.wrapped.values.first() as ObjectNode
                val commitLsn = offsetValue["commit_lsn"].asText()
                Lsn.valueOf(commitLsn)
            } catch (e: Exception) {
                log.error(e) { "Failed to parse saved LSN from offset: $offset" }
                return abortCdcSync("Invalid LSN format in saved offset")
            }

        // Validate the saved LSN is still available in SQL Server
        val isLsnValid =
            try {
                validateLsnStillAvailable(savedLsn)
            } catch (e: Exception) {
                log.error(e) { "Failed to validate LSN availability: ${savedLsn}" }
                false
            }

        if (!isLsnValid) {
            return abortCdcSync(
                "Saved LSN '${savedLsn}' is no longer available in SQL Server transaction logs"
            )
        }

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

        // Store the loaded offset for heartbeat sanitization comparison
        lastLoadedOffset = offset

        return ValidDebeziumWarmStartState(offset, schemaHistory)
    }

    // Track the last loaded offset to detect heartbeat corruption
    @Volatile private var lastLoadedOffset: DebeziumOffset? = null

    /**
     * Sanitizes the offset before saving to state to fix heartbeat-induced corruption. SQL Server
     * heartbeats reset event_serial_no to 0 and change_lsn to NULL, causing duplicate record
     * emission on subsequent syncs.
     *
     * Compares the current offset (read from Debezium) against the offset that was loaded at the
     * start of the sync.
     */
    private fun sanitizeOffset(currentOffset: DebeziumOffset): DebeziumOffset {
        val startingOffset = lastLoadedOffset ?: return currentOffset

        if (startingOffset.wrapped.size != 1 || currentOffset.wrapped.size != 1) {
            return currentOffset
        }

        val offsetKey = currentOffset.wrapped.keys.first()
        val startValue =
            startingOffset.wrapped.values.first() as? ObjectNode ?: return currentOffset
        val currentValue =
            currentOffset.wrapped.values.first() as? ObjectNode ?: return currentOffset

        val startLsn = startValue["commit_lsn"]?.asText()
        val currentLsn = currentValue["commit_lsn"]?.asText()

        // If LSN has progressed, the current offset is valid
        if (startLsn == null || currentLsn == null || startLsn != currentLsn) {
            return currentOffset
        }

        // LSN hasn't progressed - check for heartbeat regression
        val startEventSerialNo = startValue["event_serial_no"]?.asInt()
        val currentEventSerialNo = currentValue["event_serial_no"]?.asInt()
        val startChangeLsn = startValue["change_lsn"]
        val currentChangeLsn = currentValue["change_lsn"]

        val eventSerialNoRegressed =
            startEventSerialNo != null &&
                startEventSerialNo > 0 &&
                (currentEventSerialNo == null || currentEventSerialNo == 0)

        // Check if change_lsn has regressed to NULL (either JSON null or string "NULL")
        val changeLsnRegressed =
            startChangeLsn != null &&
                !startChangeLsn.isNull &&
                (currentChangeLsn == null ||
                    currentChangeLsn.isNull ||
                    (currentChangeLsn.isTextual && currentChangeLsn.asText() == "NULL"))

        if (!eventSerialNoRegressed && !changeLsnRegressed) {
            return currentOffset
        }

        // Heartbeat has corrupted the offset - restore starting values
        log.info {
            "Detected heartbeat offset regression at LSN $currentLsn. " +
                "Preserving event_serial_no=$startEventSerialNo and change_lsn=${startChangeLsn?.asText()} " +
                "from starting offset (current had event_serial_no=$currentEventSerialNo, change_lsn=${currentChangeLsn?.asText()})"
        }

        val sanitizedValue = currentValue.deepCopy()
        if (eventSerialNoRegressed && startEventSerialNo != null) {
            sanitizedValue.put("event_serial_no", startEventSerialNo)
        }
        if (changeLsnRegressed && !startChangeLsn.isNull) {
            sanitizedValue.set<JsonNode>("change_lsn", startChangeLsn)
        }

        return DebeziumOffset(mapOf(offsetKey to sanitizedValue))
    }

    /**
     * Validates if the given LSN is still available in SQL Server transaction logs. Returns true if
     * the LSN is available, false otherwise.
     */
    private fun validateLsnStillAvailable(lsn: Lsn): Boolean {
        // Use jdbcConnectionFactory which handles SSH tunneling
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { statement ->
                // Check if the LSN is within the available range
                // sys.fn_cdc_get_min_lsn returns the minimum available LSN for a capture instance
                // sys.fn_cdc_get_max_lsn returns the current maximum LSN
                val query =
                    """
                    SELECT
                        sys.fn_cdc_get_min_lsn('') AS min_lsn,
                        sys.fn_cdc_get_max_lsn() AS max_lsn
                """.trimIndent()

                statement.executeQuery(query).use { resultSet ->
                    if (resultSet.next()) {
                        val minLsnBytes = resultSet.getBytes("min_lsn")
                        val maxLsnBytes = resultSet.getBytes("max_lsn")

                        if (minLsnBytes == null || maxLsnBytes == null) {
                            log.warn { "CDC is not enabled or no LSN range available" }
                            return false
                        }

                        val minLsn = Lsn.valueOf(minLsnBytes)
                        val maxLsn = Lsn.valueOf(maxLsnBytes)

                        // Check if saved LSN is within the valid range
                        val isValid = lsn.compareTo(minLsn) >= 0 && lsn.compareTo(maxLsn) <= 0

                        if (!isValid) {
                            log.warn {
                                "Saved LSN '$lsn' is outside the available range [min: $minLsn, max: $maxLsn]. " +
                                    "Transaction logs may have been truncated."
                            }
                        }

                        return isValid
                    }
                    return false
                }
            }
        }
    }

    /**
     * Handles invalid CDC cursor position based on configured behavior. Either fails the sync or
     * resets to start fresh from current position.
     */
    private fun abortCdcSync(reason: String): InvalidDebeziumWarmStartState {
        val cdcConfig =
            configuration.incrementalReplicationConfiguration as CdcIncrementalConfiguration
        return when (cdcConfig.invalidCdcCursorPositionBehavior) {
            InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                AbortDebeziumWarmStartState(
                    "Saved offset no longer present on the server, please reset the connection. " +
                        "To prevent this, increase transaction log retention and/or increase sync frequency. " +
                        "$reason."
                )
            InvalidCdcCursorPositionBehavior.RESET_SYNC ->
                ResetDebeziumWarmStartState(
                    "Saved offset no longer present on the server. " +
                        "Automatically resetting to current position. " +
                        "WARNING: Any changes between the saved position and current position will be lost. " +
                        "$reason."
                )
        }
    }

    /**
     * Gets the current maximum LSN from SQL Server for CDC cold start. This follows the pattern
     * from the old MSSQL connector and returns the Debezium Lsn type for type safety.
     *
     * @return Lsn object representing the current maximum LSN
     * @throws IllegalStateException if CDC is not enabled or LSN cannot be retrieved
     */
    private fun getCurrentMaxLsn(): Lsn {
        // Use jdbcConnectionFactory which handles SSH tunneling
        jdbcConnectionFactory.get().use { connection: Connection ->
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
        val tunnelSession: TunnelSession = jdbcConnectionFactory.ensureTunnelSession()

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
            .withDatabase("hostname", tunnelSession.address.hostName)
            .withDatabase("port", tunnelSession.address.port.toString())
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
            .with(
                AIRBYTE_HEARTBEAT_TIMEOUT_SECONDS,
                configuration.incrementalReplicationConfiguration.initialWaitingSeconds
                    .toSeconds()
                    .toString()
            )
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
