/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumInput
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumState
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mysql.CdcIncrementalConfiguration
import io.airbyte.integrations.source.mysql.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.mysql.MysqlSourceConfiguration
import io.airbyte.integrations.source.mysql.cdc.converters.MySQLDateTimeConverter
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.debezium.connector.mysql.MySqlConnector
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
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

@Singleton
class MySqlDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: MysqlSourceConfiguration,
    random: Random = Random.Default,
) : DebeziumOperations<MySqlPosition> {
    private val log = KotlinLogging.logger {}

    override fun toAirbyteRecordMessage(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue
    ): AirbyteRecordMessage {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull

        airbyteRecord.meta.changes.clear()
        airbyteRecord.stream = source["table"].asText()
        airbyteRecord.namespace = source["db"].asText()
        val transactionMillis: Long = source["ts_ms"].asLong()
        val transactionOffsetDateTime: OffsetDateTime =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(transactionMillis), ZoneOffset.UTC)
        val transactionTimestampJsonNode: JsonNode =
            OffsetDateTimeCodec.encode(transactionOffsetDateTime)

        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
        data.set<JsonNode>(CommonMetaField.CDC_UPDATED_AT.id, transactionTimestampJsonNode)
        data.set<JsonNode>(
            CommonMetaField.CDC_DELETED_AT.id,
            if (isDelete) transactionTimestampJsonNode else Jsons.nullNode(),
        )
        return airbyteRecord.withData(data)
    }

    /**
     * Checks if GTIDs from previously saved state (debeziumInput) are still valid on DB. And also
     * check if binlog exists or not.
     *
     * Validate is not supposed to perform on synthetic state.
     */
    private fun validate(debeziumState: DebeziumState): CdcStateValidateResult {
        val (_: MySqlPosition, gtidSet: String?) = queryPositionAndGtids()
        if (gtidSet.isNullOrEmpty()) {
            return abortCdcSync()
        }
        val savedStateOffset: SavedOffset = parseSavedOffset(debeziumState)

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
            if (!newGtidSet.subtract(purgedGtidSet).equals(newGtidSet)) {
                log.info {
                    "Connector has not seen GTIDs $newGtidSet, but MySQL server has purged $purgedGtidSet"
                }
                return abortCdcSync()
            }
        }
        val existingLogFiles: List<String> = getBinaryLogFileNames()
        val found = existingLogFiles.contains(savedStateOffset.position.fileName)
        if (!found) {
            log.info {
                "Connector last known binlog file ${savedStateOffset.position.fileName} is not found in the server"
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
                log.info { "Current position is invalid, aborting sync." }
                CdcStateValidateResult.INVALID_ABORT
            }
            InvalidCdcCursorPositionBehavior.RESET_SYNC -> {
                log.info { "Current position is invalid, resetting sync." }
                CdcStateValidateResult.INVALID_RESET
            }
        }
    }

    private fun parseSavedOffset(debeziumState: DebeziumState): SavedOffset {
        val position: MySqlPosition = position(debeziumState.offset)
        val gtidSet: String? = debeziumState.offset.wrapped.values.first()["gtids"]?.asText()
        return SavedOffset(position, gtidSet)
    }

    data class SavedOffset(val position: MySqlPosition, val gtidSet: String?)

    enum class CdcStateValidateResult {
        VALID,
        INVALID_ABORT,
        INVALID_RESET
    }

    private val airbyteRecord = AirbyteRecordMessage().withMeta(AirbyteRecordMessageMeta())

    override fun position(offset: DebeziumOffset): MySqlPosition {
        if (offset.wrapped.size != 1) {
            throw ConfigErrorException("Expected exactly 1 key in $offset")
        }
        val offsetValue: ObjectNode = offset.wrapped.values.first() as ObjectNode
        return MySqlPosition(offsetValue["file"].asText(), offsetValue["pos"].asLong())
    }

    override fun position(recordValue: DebeziumRecordValue): MySqlPosition? {
        val file: JsonNode = recordValue.source["file"]?.takeIf { it.isTextual } ?: return null
        val pos: JsonNode = recordValue.source["pos"]?.takeIf { it.isIntegralNumber } ?: return null
        return MySqlPosition(file.asText(), pos.asLong())
    }

    override fun position(sourceRecord: SourceRecord): MySqlPosition? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val file: Any = offset["file"] ?: return null
        val pos: Long = offset["pos"] as? Long ?: return null
        return MySqlPosition(file.toString(), pos)
    }

    override fun synthesize(): DebeziumInput {
        val (mySqlPosition: MySqlPosition, gtidSet: String?) = queryPositionAndGtids()
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
                put("file", mySqlPosition.fileName)
                put("pos", mySqlPosition.position)
                if (gtidSet != null) {
                    put("gtids", gtidSet)
                }
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        val state = DebeziumState(offset, schemaHistory = null)
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    private fun queryPositionAndGtids(): Pair<MySqlPosition, String?> {
        val file = Field("File", StringFieldType)
        val pos = Field("Position", LongFieldType)
        val gtids = Field("Executed_Gtid_Set", StringFieldType)
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SHOW MASTER STATUS"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    val mySqlPosition =
                        MySqlPosition(
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
                        return mySqlPosition to null
                    }
                    val gtidSet: String? =
                        rs.getString(gtids.id)
                            ?.takeUnless { rs.wasNull() || it.isBlank() }
                            ?.trim()
                            ?.replace("\n", "")
                            ?.replace("\r", "")
                    return mySqlPosition to gtidSet
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
        val logNameField = Field("Log_name", StringFieldType)
        return jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SHOW BINARY LOGS"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    generateSequence { if (rs.next()) rs.getString(logNameField.id) else null }
                        .toList()
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
                throw ConfigErrorException("Current position is invalid.")
            }
            return synthesize()
        }

        val properties: Map<String, String> =
            DebeziumPropertiesBuilder().with(commonProperties).withStreams(streams).buildMap()
        return DebeziumInput(properties, debeziumState, isSynthetic = false)
    }

    private fun deserializeDebeziumState(opaqueStateValue: OpaqueStateValue): DebeziumState {
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
                val compressedBytes: ByteArray =
                    Jsons.readValue(schemaNode.textValue(), ByteArray::class.java)
                GZIPInputStream(ByteArrayInputStream(compressedBytes))
                    .reader(Charsets.UTF_8)
                    .readText()
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
                GZIPOutputStream(baos).writer(Charsets.UTF_8).use { it.write(uncompressedString) }
                stateNode.put(MYSQL_DB_HISTORY, baos.toByteArray())
            }
        }
        return Jsons.objectNode().apply { set<JsonNode>(STATE, stateNode) }
    }

    val databaseName: String = configuration.namespaces.first()
    val serverID: Int = random.nextInt(MIN_SERVER_ID..MAX_SERVER_ID)

    val commonProperties: Map<String, String> by lazy {
        val tunnelSession: TunnelSession = jdbcConnectionFactory.ensureTunnelSession()
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(MySqlConnector::class.java)
            .withDebeziumName(databaseName)
            .withHeartbeats(configuration.debeziumHeartbeatInterval)
            // This to make sure that binary data represented as a base64-encoded String.
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
            .with("binary.handling.mode", "base64")
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
            .with("snapshot.mode", "when_needed")
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-locking-mode
            // This is to make sure other database clients are allowed to write to a table while
            // Airbyte is taking a snapshot. There is a risk involved that if any database client
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
            .with("converters", "datetime")
            .with(
                "datetime.type",
                MySQLDateTimeConverter::class.java.getName(),
            )
            // TODO: add missing properties, like MySQL converters, etc. Do a full audit.
            .buildMap()
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
    }
}
