/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
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
import io.debezium.connector.postgresql.PostgresConnector
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
class PostgresV2SourceDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: PostgresV2SourceConfiguration,
    random: Random = Random.Default,
) :
    CdcPartitionsCreatorDebeziumOperations<PostgresV2SourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<PostgresV2SourceCdcPosition> {
    private val log = KotlinLogging.logger {}
    private val cdcIncrementalConfiguration: CdcIncrementalConfiguration by lazy {
        configuration.incrementalConfiguration as CdcIncrementalConfiguration
    }

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
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode

        val resultRow: NativeRecordPayload = mutableMapOf()
        for (field in stream.schema) {
            when (field.type.airbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER,
                LeafAirbyteSchemaType.NUMBER -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        val bigDecimal = BigDecimal(textNode.textValue()).stripTrailingZeros()
                        data.put(field.id, bigDecimal)
                    }
                }
                LeafAirbyteSchemaType.JSONB -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        data.set<JsonNode>(field.id, Jsons.readTree(textNode.textValue()))
                    }
                }
                LeafAirbyteSchemaType.BINARY -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        val bytes: ByteArray =
                            Base64.decodeBase64(textNode.textValue().toByteArray())
                        data.set<JsonNode>(field.id, Jsons.binaryNode(bytes))
                    }
                }
                else -> {
                    /* no-op */
                }
            }
            data[field.id] ?: continue
            when (data[field.id]) {
                is NullNode -> {
                    resultRow[field.id] = FieldValueEncoder(null, NullCodec)
                }
                else -> {
                    val codec: JsonCodec<*> =
                        when (field.type) {
                            FloatFieldType ->
                                if (data[field.id] is com.fasterxml.jackson.databind.node.FloatNode)
                                    FloatCodec
                                else DoubleCodec
                            else -> field.type.jsonEncoder as JsonCodec<*>
                        }
                    @Suppress("UNCHECKED_CAST")
                    resultRow[field.id] =
                        FieldValueEncoder(
                            codec.decode(data[field.id]),
                            codec as JsonCodec<Any>,
                        )
                }
            }
        }
        // Set _ab_cdc_updated_at and _ab_cdc_deleted_at meta-field values.
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

        // Set _ab_cdc_lsn meta-field value.
        val lsn = source["lsn"].asLong()
        val position = PostgresV2SourceCdcPosition.fromLsn(lsn)

        resultRow[PostgresV2SourceCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                position.lsnString,
                PostgresV2SourceCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>
            )

        // Set the _ab_cdc_cursor meta-field value.
        resultRow[PostgresV2SourceCdcMetaFields.CDC_CURSOR.id] =
            FieldValueEncoder(
                position.cursorValue,
                PostgresV2SourceCdcMetaFields.CDC_CURSOR.type.jsonEncoder as JsonEncoder<Any>
            )

        // Return a DeserializedRecord instance.
        return DeserializedRecord(resultRow, emptyMap())
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["schema"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

    override fun deserializeState(
        opaqueStateValue: OpaqueStateValue,
    ): DebeziumWarmStartState {
        val debeziumState: UnvalidatedDeserializedState =
            try {
                deserializeStateUnvalidated(opaqueStateValue)
            } catch (e: Exception) {
                log.error(e) { "Error deserializing incumbent state value." }
                return AbortDebeziumWarmStartState(
                    "Error deserializing incumbent state value: ${e.message}"
                )
            }
        return validate(debeziumState)
    }

    /**
     * Validates the deserialized state against the current PostgreSQL replication slot. Checks if
     * the saved LSN is still valid (not behind the confirmed flush LSN).
     */
    private fun validate(debeziumState: UnvalidatedDeserializedState): DebeziumWarmStartState {
        val savedPosition: PostgresV2SourceCdcPosition = position(debeziumState.offset)

        // Query the replication slot to get the confirmed flush LSN
        val slotInfo = queryReplicationSlotInfo()
        if (slotInfo == null) {
            return abortCdcSync(
                "Replication slot '${cdcIncrementalConfiguration.replicationSlot}' not found"
            )
        }

        // Check if saved LSN is behind the confirmed flush LSN
        if (
            slotInfo.confirmedFlushLsn != null && savedPosition.lsn < slotInfo.confirmedFlushLsn.lsn
        ) {
            return abortCdcSync(
                "Saved LSN (${savedPosition.lsnString}) is behind the confirmed flush LSN (${slotInfo.confirmedFlushLsn.lsnString})"
            )
        }

        return ValidDebeziumWarmStartState(debeziumState.offset, debeziumState.schemaHistory)
    }

    private fun abortCdcSync(reason: String): InvalidDebeziumWarmStartState =
        when (cdcIncrementalConfiguration.invalidCdcCursorPositionBehavior) {
            InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                AbortDebeziumWarmStartState(
                    "Saved offset no longer present on the server, please reset the connection, " +
                        "and then increase WAL retention. $reason."
                )
            InvalidCdcCursorPositionBehavior.RESET_SYNC ->
                ResetDebeziumWarmStartState(
                    "Saved offset no longer present on the server. $reason."
                )
        }

    data class ReplicationSlotInfo(
        val slotName: String,
        val plugin: String,
        val database: String,
        val confirmedFlushLsn: PostgresV2SourceCdcPosition?,
        val restartLsn: PostgresV2SourceCdcPosition?,
    )

    private fun queryReplicationSlotInfo(): ReplicationSlotInfo? {
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql =
                    """
                    SELECT slot_name, plugin, database, confirmed_flush_lsn, restart_lsn
                    FROM pg_replication_slots
                    WHERE slot_name = '${cdcIncrementalConfiguration.replicationSlot}'
                """.trimIndent()
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) return null
                    val confirmedFlushLsnStr = rs.getString("confirmed_flush_lsn")
                    val restartLsnStr = rs.getString("restart_lsn")
                    return ReplicationSlotInfo(
                        slotName = rs.getString("slot_name"),
                        plugin = rs.getString("plugin"),
                        database = rs.getString("database"),
                        confirmedFlushLsn =
                            confirmedFlushLsnStr?.let {
                                PostgresV2SourceCdcPosition.fromLsnString(it)
                            },
                        restartLsn =
                            restartLsnStr?.let { PostgresV2SourceCdcPosition.fromLsnString(it) },
                    )
                }
            }
        }
    }

    override fun position(offset: DebeziumOffset): PostgresV2SourceCdcPosition =
        Companion.position(offset)

    override fun position(recordValue: DebeziumRecordValue): PostgresV2SourceCdcPosition? {
        val lsn: JsonNode = recordValue.source["lsn"]?.takeIf { it.isIntegralNumber } ?: return null
        return PostgresV2SourceCdcPosition.fromLsn(lsn.asLong())
    }

    override fun position(sourceRecord: SourceRecord): PostgresV2SourceCdcPosition? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val lsn: Long = offset["lsn"] as? Long ?: return null
        return PostgresV2SourceCdcPosition.fromLsn(lsn)
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        val currentLsn: PostgresV2SourceCdcPosition = queryCurrentLsn()
        val topicPrefixName: String = DebeziumPropertiesBuilder.sanitizeTopicPrefix(databaseName)
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", topicPrefixName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_usec", timestamp.toEpochMilli() * 1000)
                put("lsn", currentLsn.lsn)
                put("txId", 0)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        return offset
    }

    private fun queryCurrentLsn(): PostgresV2SourceCdcPosition {
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SELECT pg_current_wal_lsn()"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    val lsnString = rs.getString(1)
                    return PostgresV2SourceCdcPosition.fromLsnString(lsnString)
                }
            }
        }
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder()
            .with(commonProperties)
            // Use 'exported' snapshot mode for cold start to capture the current LSN
            .with("snapshot.mode", "exported")
            .buildMap()

    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder().with(commonProperties).withStreams(streams).buildMap()

    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue {
        val stateNode: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        stateNode.set<JsonNode>(POSTGRES_CDC_OFFSET, offsetNode)
        // Serialize schema history.
        if (schemaHistory != null) {
            val uncompressedString: String =
                schemaHistory.wrapped.joinToString(separator = "\n") {
                    DocumentWriter.defaultWriter().write(it.document())
                }
            if (uncompressedString.length <= MAX_UNCOMPRESSED_LENGTH) {
                stateNode.put(POSTGRES_DB_HISTORY, uncompressedString)
            } else {
                stateNode.put(IS_COMPRESSED, true)
                val baos = ByteArrayOutputStream()
                val builder = StringBuilder()
                GZIPOutputStream(baos).writer(Charsets.UTF_8).use { it.write(uncompressedString) }

                builder.append("\"")
                builder.append(Base64.encodeBase64(baos.toByteArray()).toString(Charsets.UTF_8))
                builder.append("\"")

                stateNode.put(POSTGRES_DB_HISTORY, builder.toString())
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
                .withConnector(PostgresConnector::class.java)
                .withDebeziumName(databaseName)
                .withHeartbeats(configuration.debeziumHeartbeatInterval)
                // PostgreSQL-specific Debezium settings
                .with("plugin.name", "pgoutput")
                .with("slot.name", cdcIncrementalConfiguration.replicationSlot)
                .with("publication.name", cdcIncrementalConfiguration.publication)
                .with("publication.autocreate.mode", "disabled")
                // This is to make sure that binary data represented as a base64-encoded String.
                .with("binary.handling.mode", "base64")
                // This is to make sure that numbers are represented as strings.
                .with("decimal.handling.mode", "string")
                // This is to make sure that temporal data is represented without loss of precision.
                .with("time.precision.mode", "adaptive_time_microseconds")
                // Don't include unknown data types
                .with("include.unknown.datatypes", "false")
                // Schema changes are not included
                .with("include.schema.changes", "false")
                // No snapshot locking to allow concurrent writes
                .with("snapshot.locking.mode", "none")
                .withDatabase(configuration.jdbcProperties)
                .withDatabase("hostname", tunnelSession.address.hostName)
                .withDatabase("port", tunnelSession.address.port.toString())
                .withDatabase("dbname", databaseName)
                .withOffset()
                .withSchemaHistory()

        // Add schema filtering if namespaces are specified
        val schemas = configuration.namespaces.joinToString(",")
        dbzPropertiesBuilder.with("schema.include.list", schemas)

        dbzPropertiesBuilder.buildMap()
    }

    companion object {
        // Constants defining a range for the random value picked for the unique connector ID
        const val MIN_SERVER_ID = 5400
        const val MAX_SERVER_ID = 6400

        const val MAX_UNCOMPRESSED_LENGTH = 1024 * 1024
        const val STATE = "state"
        const val POSTGRES_CDC_OFFSET = "postgres_cdc_offset"
        const val POSTGRES_DB_HISTORY = "postgres_db_history"
        const val IS_COMPRESSED = "is_compressed"

        /**
         * The name of the Debezium property that contains the unique name for the Debezium
         * connector.
         */
        const val CONNECTOR_NAME_PROPERTY: String = "name"

        /** Configuration for offset state key/value converters. */
        val INTERNAL_CONVERTER_CONFIG: Map<String, String> =
            java.util.Map.of(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString())

        internal fun deserializeStateUnvalidated(
            opaqueStateValue: OpaqueStateValue
        ): UnvalidatedDeserializedState {
            val stateNode: ObjectNode = opaqueStateValue[STATE] as ObjectNode
            // Deserialize offset.
            val offsetNode: ObjectNode = stateNode[POSTGRES_CDC_OFFSET] as ObjectNode
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
                stateNode[POSTGRES_DB_HISTORY] ?: return UnvalidatedDeserializedState(offset)
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
            return UnvalidatedDeserializedState(offset, DebeziumSchemaHistory(schemaHistoryList))
        }

        data class UnvalidatedDeserializedState(
            val offset: DebeziumOffset,
            val schemaHistory: DebeziumSchemaHistory? = null,
        )

        internal fun position(offset: DebeziumOffset): PostgresV2SourceCdcPosition {
            if (offset.wrapped.size != 1) {
                throw ConfigErrorException("Expected exactly 1 key in $offset")
            }
            val offsetValue: ObjectNode = offset.wrapped.values.first() as ObjectNode
            return PostgresV2SourceCdcPosition.fromLsn(offsetValue["lsn"].asLong())
        }
    }
}
