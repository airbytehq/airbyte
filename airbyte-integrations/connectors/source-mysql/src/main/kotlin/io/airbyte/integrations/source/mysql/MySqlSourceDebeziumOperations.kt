/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.CdcPartitionsCreator.OffsetInvalidNeedsResyncIllegalStateException
import io.airbyte.cdk.read.cdc.DebeziumInput
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.MySqlConnector
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import kotlin.random.Random
import kotlin.random.nextInt
import org.apache.kafka.connect.json.JsonConverterConfig
import org.apache.kafka.connect.source.SourceRecord
import org.apache.mina.util.Base64

@Singleton
class MySqlSourceDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: MySqlSourceConfiguration,
    random: Random = Random.Default,
) : DebeziumOperations<MySqlSourceCdcPosition> {
    private val log = KotlinLogging.logger {}

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull
        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
        // Turn string representations of numbers into BigDecimals.
        for (field in stream.schema) {
            when (field.type.airbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER,
                LeafAirbyteSchemaType.NUMBER -> {
                    val textNode: TextNode = data[field.id] as? TextNode ?: continue
                    val bigDecimal = BigDecimal(textNode.textValue()).stripTrailingZeros()
                    data.put(field.id, bigDecimal)
                }
                LeafAirbyteSchemaType.JSONB -> {
                    val textNode: TextNode = data[field.id] as? TextNode ?: continue
                    data.set<JsonNode>(field.id, Jsons.readTree(textNode.textValue()))
                }
                else -> continue
            }
        }
        // Set _ab_cdc_updated_at and _ab_cdc_deleted_at meta-field values.
        val transactionMillis: Long = source["ts_ms"].asLong()
        val transactionOffsetDateTime: OffsetDateTime =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(transactionMillis), ZoneOffset.UTC)
        val transactionTimestampJsonNode: JsonNode =
            OffsetDateTimeCodec.encode(transactionOffsetDateTime)
        data.set<JsonNode>(
            CommonMetaField.CDC_UPDATED_AT.id,
            transactionTimestampJsonNode,
        )
        data.set<JsonNode>(
            CommonMetaField.CDC_DELETED_AT.id,
            if (isDelete) transactionTimestampJsonNode else Jsons.nullNode(),
        )
        // Set _ab_cdc_log_file and _ab_cdc_log_pos meta-field values.
        val position = MySqlSourceCdcPosition(source["file"].asText(), source["pos"].asLong())
        data.set<JsonNode>(
            MySqlSourceCdcMetaFields.CDC_LOG_FILE.id,
            TextCodec.encode(position.fileName)
        )
        data.set<JsonNode>(
            MySqlSourceCdcMetaFields.CDC_LOG_POS.id,
            LongCodec.encode(position.position)
        )
        // Set the _ab_cdc_cursor meta-field value.
        data.set<JsonNode>(
            MySqlSourceCdcMetaFields.CDC_CURSOR.id,
            LongCodec.encode(position.cursorValue)
        )
        // Return a DeserializedRecord instance.
        return DeserializedRecord(data, changes = emptyMap())
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["db"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

    /**
     * Checks if GTIDs from previously saved state (debeziumInput) are still valid on DB. And also
     * check if binlog exists or not.
     *
     * Validate is not supposed to perform on synthetic state.
     */
    private fun validate(debeziumState: DebeziumState): CdcStateValidateResult {
        val savedStateOffset: SavedOffset = parseSavedOffset(debeziumState)
        val (_: MySqlSourceCdcPosition, gtidSet: String?) = queryPositionAndGtids()
        if (gtidSet.isNullOrEmpty() && !savedStateOffset.gtidSet.isNullOrEmpty()) {
            log.info {
                "Connector used GTIDs previously, but MySQL server does not know of any GTIDs or they are not enabled"
            }
            return abortCdcSync()
        }

        val savedGtidSet = MySqlGtidSet(savedStateOffset.gtidSet)
        val availableGtidSet = MySqlGtidSet(gtidSet)
        if (!savedGtidSet.isContainedWithin(availableGtidSet)) {
            log.info {
                "Connector last known GTIDs are $savedGtidSet, but MySQL server only has $availableGtidSet"
            }
            return abortCdcSync()
        }

        // newGtidSet is gtids from server that hasn't been seen by this connector yet. If the set
        // exists, check that they are not purged, or we may lose those data.
        val newGtidSet = availableGtidSet.subtract(savedGtidSet)
        if (!newGtidSet.isEmpty) {
            val purgedGtidSet = queryPurgedIds()
            if (!purgedGtidSet.isEmpty && !newGtidSet.subtract(purgedGtidSet).equals(newGtidSet)) {
                log.info {
                    "Connector has not seen GTIDs $newGtidSet, but MySQL server has purged $purgedGtidSet"
                }
                return abortCdcSync()
            }
        }
        if (!savedGtidSet.isEmpty) {
            // If the connector has saved GTID set, we will use that to validate and skip
            // binlog validation. GTID and binlog works in an independent way to ensure data
            // integrity where GTID is for storing transactions and binlog is for storing changes
            // in DB.
            return CdcStateValidateResult.VALID
        }
        val existingLogFiles: List<String> = getBinaryLogFileNames()
        val found = existingLogFiles.contains(savedStateOffset.position.fileName)
        if (!found) {
            log.info {
                "Connector last known binlog file ${savedStateOffset.position.fileName} is " +
                    "not found in the server. Server has $existingLogFiles"
            }
            return abortCdcSync()
        }
        return CdcStateValidateResult.VALID
    }

    private fun abortCdcSync(): CdcStateValidateResult {
        val cdcIncrementalConfiguration: CdcIncrementalConfiguration =
            configuration.incrementalConfiguration as CdcIncrementalConfiguration
        return when (cdcIncrementalConfiguration.invalidCdcCursorPositionBehavior) {
            InvalidCdcCursorPositionBehavior.FAIL_SYNC -> {
                log.warn { "Saved offset no longer present on the server. aborting sync." }
                CdcStateValidateResult.INVALID_ABORT
            }
            InvalidCdcCursorPositionBehavior.RESET_SYNC -> {
                log.warn {
                    "Saved offset no longer present on the server, Airbyte is going to trigger a sync from scratch."
                }
                CdcStateValidateResult.INVALID_RESET
            }
        }
    }

    private fun parseSavedOffset(debeziumState: DebeziumState): SavedOffset {
        val position: MySqlSourceCdcPosition = position(debeziumState.offset)
        val gtidSet: String? = debeziumState.offset.wrapped.values.first()["gtids"]?.asText()
        return SavedOffset(position, gtidSet)
    }

    data class SavedOffset(val position: MySqlSourceCdcPosition, val gtidSet: String?)

    enum class CdcStateValidateResult {
        VALID,
        INVALID_ABORT,
        INVALID_RESET
    }

    override fun position(offset: DebeziumOffset): MySqlSourceCdcPosition =
        Companion.position(offset)

    override fun position(recordValue: DebeziumRecordValue): MySqlSourceCdcPosition? {
        val file: JsonNode = recordValue.source["file"]?.takeIf { it.isTextual } ?: return null
        val pos: JsonNode = recordValue.source["pos"]?.takeIf { it.isIntegralNumber } ?: return null
        return MySqlSourceCdcPosition(file.asText(), pos.asLong())
    }

    override fun position(sourceRecord: SourceRecord): MySqlSourceCdcPosition? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val file: Any = offset["file"] ?: return null
        val pos: Long = offset["pos"] as? Long ?: return null
        return MySqlSourceCdcPosition(file.toString(), pos)
    }

    override fun synthesize(): DebeziumInput {
        val (mySqlSourceCdcPosition: MySqlSourceCdcPosition, gtidSet: String?) =
            queryPositionAndGtids()
        val topicPrefixName: String = DebeziumPropertiesBuilder.sanitizeTopicPrefix(databaseName)
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", topicPrefixName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_sec", timestamp.epochSecond)
                put("file", mySqlSourceCdcPosition.fileName)
                put("pos", mySqlSourceCdcPosition.position)
                if (gtidSet != null) {
                    put("gtids", gtidSet)
                }
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        val state = DebeziumState(offset, schemaHistory = null)
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    private fun queryPositionAndGtids(): Pair<MySqlSourceCdcPosition, String?> {
        val file = Field("File", StringFieldType)
        val pos = Field("Position", LongFieldType)
        val gtids = Field("Executed_Gtid_Set", StringFieldType)
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SHOW MASTER STATUS"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    val mySqlSourceCdcPosition =
                        MySqlSourceCdcPosition(
                            fileName = rs.getString(file.id)?.takeUnless { rs.wasNull() }
                                    ?: throw ConfigErrorException(
                                        "No value for ${file.id} in: $sql",
                                    ),
                            position = rs.getLong(pos.id).takeUnless { rs.wasNull() || it <= 0 }
                                    ?: throw ConfigErrorException(
                                        "No value for ${pos.id} in: $sql",
                                    ),
                        )
                    if (rs.metaData.columnCount <= 4) {
                        // This value exists only in MySQL 5.6.5 or later.
                        return mySqlSourceCdcPosition to null
                    }
                    val gtidSet: String? =
                        rs.getString(gtids.id)
                            ?.takeUnless { rs.wasNull() || it.isBlank() }
                            ?.trim()
                            ?.replace("\n", "")
                            ?.replace("\r", "")
                    return mySqlSourceCdcPosition to gtidSet
                }
            }
        }
    }

    private fun queryPurgedIds(): MySqlGtidSet {
        val purgedGtidField = Field("@@global.gtid_purged", StringFieldType)
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SELECT @@global.gtid_purged"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    return MySqlGtidSet(rs.getString(purgedGtidField.id))
                }
            }
        }
    }

    private fun getBinaryLogFileNames(): List<String> {
        // Very old MySQL version (4.x) has different output of SHOW BINARY LOGS output.
        return jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SHOW BINARY LOGS"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    generateSequence { if (rs.next()) rs.getString(1) else null }.toList()
                }
            }
        }
    }

    override fun deserialize(
        opaqueStateValue: OpaqueStateValue,
        streams: List<Stream>
    ): DebeziumInput {
        val debeziumState: DebeziumState =
            try {
                deserializeDebeziumState(opaqueStateValue)
            } catch (e: Exception) {
                throw ConfigErrorException("Error deserializing $opaqueStateValue", e)
            }
        val cdcValidationResult = validate(debeziumState)
        if (cdcValidationResult != CdcStateValidateResult.VALID) {
            if (cdcValidationResult == CdcStateValidateResult.INVALID_ABORT) {
                throw ConfigErrorException(
                    "Saved offset no longer present on the server. Please reset the connection, and then increase binlog retention and/or increase sync frequency."
                )
            }
            if (cdcValidationResult == CdcStateValidateResult.INVALID_RESET) {
                throw OffsetInvalidNeedsResyncIllegalStateException()
            }
            return synthesize(streams)
        }

        val properties: Map<String, String> =
            DebeziumPropertiesBuilder().with(commonProperties).buildMap()
        return DebeziumInput(properties, debeziumState, isSynthetic = false)
    }

    override fun serialize(debeziumState: DebeziumState): OpaqueStateValue {
        val stateNode: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in debeziumState.offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        stateNode.set<JsonNode>(MYSQL_CDC_OFFSET, offsetNode)
        // Serialize schema history.
        val schemaHistory: List<HistoryRecord>? = debeziumState.schemaHistory?.wrapped
        if (schemaHistory != null) {
            val uncompressedString: String =
                schemaHistory.joinToString(separator = "\n") {
                    DocumentWriter.defaultWriter().write(it.document())
                }
            if (uncompressedString.length <= MAX_UNCOMPRESSED_LENGTH) {
                stateNode.put(MYSQL_DB_HISTORY, uncompressedString)
            } else {
                stateNode.put(IS_COMPRESSED, true)
                val baos = ByteArrayOutputStream()
                val builder = StringBuilder()
                GZIPOutputStream(baos).writer(Charsets.UTF_8).use { it.write(uncompressedString) }

                builder.append("\"")
                builder.append(Base64.encodeBase64(baos.toByteArray()).toString(Charsets.UTF_8))
                builder.append("\"")

                stateNode.put(MYSQL_DB_HISTORY, builder.toString())
            }
        }
        return Jsons.objectNode().apply { set<JsonNode>(STATE, stateNode) }
    }

    val databaseName: String = configuration.namespaces.first()
    val serverID: Int = random.nextInt(MIN_SERVER_ID..MAX_SERVER_ID)

    val commonProperties: Map<String, String> by lazy {
        val tunnelSession: TunnelSession = jdbcConnectionFactory.ensureTunnelSession()
        val dbzPropertiesBuilder =
            DebeziumPropertiesBuilder()
                .withDefault()
                .withConnector(MySqlConnector::class.java)
                .withDebeziumName(databaseName)
                .withHeartbeats(configuration.debeziumHeartbeatInterval)
                // This to make sure that binary data represented as a base64-encoded String.
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
                .with("binary.handling.mode", "base64")
                // This is to make sure that numbers are represented as strings.
                .with("decimal.handling.mode", "string")
                // This is to make sure that temporal data is represented without loss of precision.
                .with("time.precision.mode", "adaptive_time_microseconds")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
                .with("snapshot.mode", "initial_only")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-locking-mode
                // This is to make sure other database clients are allowed to write to a table while
                // Airbyte is taking a snapshot. There is a risk involved that if any database
                // client
                // makes a schema change then the sync might break
                .with("snapshot.locking.mode", "none")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-include-schema-changes
                .with("include.schema.changes", "false")
                .with(
                    "connect.keep.alive.interval.ms",
                    configuration.debeziumKeepAliveInterval.toMillis().toString(),
                )
                .withDatabase(configuration.jdbcProperties)
                .withDatabase("hostname", tunnelSession.address.hostName)
                .withDatabase("port", tunnelSession.address.port.toString())
                .withDatabase("dbname", databaseName)
                .withDatabase("server.id", serverID.toString())
                .withDatabase("include.list", databaseName)
                .withOffset()
                .withSchemaHistory()
                .withConverters(
                    MySqlSourceCdcBooleanConverter::class,
                    MySqlSourceCdcTemporalConverter::class
                )

        val serverTimezone: String? =
            (configuration.incrementalConfiguration as CdcIncrementalConfiguration).serverTimezone
        if (!serverTimezone.isNullOrBlank()) {
            dbzPropertiesBuilder.with("database.connectionTimezone", serverTimezone)
        }
        dbzPropertiesBuilder.buildMap()
    }

    val syntheticProperties: Map<String, String> by lazy {
        DebeziumPropertiesBuilder()
            .with(commonProperties)
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
            // We use the recovery property cause using this mode will instruct Debezium to
            // construct the db schema history. Note that we used to use schema_only_recovery mode
            // instead, but this mode has been deprecated.
            .with("snapshot.mode", "recovery")
            .withStreams(listOf())
            .buildMap()
    }

    companion object {
        // Constants defining a range for the random value picked for the database.server.id
        // Debezium property which uniquely identifies the binlog consumer.
        // https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-property-database-server-id
        const val MIN_SERVER_ID = 5400
        const val MAX_SERVER_ID = 6400

        const val MAX_UNCOMPRESSED_LENGTH = 1024 * 1024
        const val STATE = "state"
        const val MYSQL_CDC_OFFSET = "mysql_cdc_offset"
        const val MYSQL_DB_HISTORY = "mysql_db_history"
        const val IS_COMPRESSED = "is_compressed"

        /**
         * The name of the Debezium property that contains the unique name for the Debezium
         * connector.
         */
        const val CONNECTOR_NAME_PROPERTY: String = "name"

        /** Configuration for offset state key/value converters. */
        val INTERNAL_CONVERTER_CONFIG: Map<String, String> =
            java.util.Map.of(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString())

        internal fun deserializeDebeziumState(opaqueStateValue: OpaqueStateValue): DebeziumState {
            val stateNode: ObjectNode = opaqueStateValue[STATE] as ObjectNode
            // Deserialize offset.
            val offsetNode: ObjectNode = stateNode[MYSQL_CDC_OFFSET] as ObjectNode
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
            // Deserialize schema history.
            val schemaNode: JsonNode =
                stateNode[MYSQL_DB_HISTORY] ?: return DebeziumState(offset, schemaHistory = null)
            val isCompressed: Boolean = stateNode[IS_COMPRESSED]?.asBoolean() ?: false
            val uncompressedString: String =
                if (isCompressed) {
                    val textValue: String = schemaNode.textValue()
                    val compressedBytes: ByteArray =
                        textValue.substring(1, textValue.length - 1).toByteArray(Charsets.UTF_8)
                    val decoded = Base64.decodeBase64(compressedBytes)

                    GZIPInputStream(ByteArrayInputStream(decoded)).reader(Charsets.UTF_8).readText()
                } else {
                    schemaNode.textValue()
                }
            val schemaHistoryList: List<HistoryRecord> =
                uncompressedString
                    .lines()
                    .filter { it.isNotBlank() }
                    .map { HistoryRecord(DocumentReader.defaultReader().read(it)) }
            return DebeziumState(offset, DebeziumSchemaHistory(schemaHistoryList))
        }

        internal fun position(offset: DebeziumOffset): MySqlSourceCdcPosition {
            if (offset.wrapped.size != 1) {
                throw ConfigErrorException("Expected exactly 1 key in $offset")
            }
            val offsetValue: ObjectNode = offset.wrapped.values.first() as ObjectNode
            return MySqlSourceCdcPosition(offsetValue["file"].asText(), offsetValue["pos"].asLong())
        }
    }
}
