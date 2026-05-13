/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.ArrayDecoder
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange
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
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.PostgresConnector
import io.debezium.connector.postgresql.connection.Lsn
import io.debezium.time.Conversions
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import kotlin.collections.component1
import kotlin.collections.component2
import org.apache.kafka.connect.source.SourceRecord

@Singleton
class PostgresSourceDebeziumOperations(
    private val config: PostgresSourceConfiguration,
    private val connectionFactory: PostgresSourceJdbcConnectionFactory,
    private val replicationSlotManager: ReplicationSlotManager,
    private val startupState: StartupState?,
) :
    CdcPartitionsCreatorDebeziumOperations<PostgresSourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<PostgresSourceCdcPosition> {

    private val log = KotlinLogging.logger {}
    private val cdcConfig: CdcIncrementalConfiguration by lazy { config.cdc!! }

    companion object {
        const val STATE = "state"
        const val SERVER = "server"
        const val LSN = "lsn"
        const val LSN_PROC = "lsn_proc"
        const val LSN_COMMIT = "lsn_commit"

        internal fun deserializeStateUnvalidated(
            opaqueStateValue: OpaqueStateValue
        ): DebeziumOffset {
            // {
            //     "state": {
            //         "[\"postgres\",{\"server\":\"postgres\"}]":
            //              "{\"lsn_proc\":3575761602216,\"lsn\":3575761602216}"
            //     }
            // }
            val stateNode: ObjectNode = opaqueStateValue[STATE] as ObjectNode
            check(stateNode.size() == 1) { "State value has unexpected format: $opaqueStateValue" }
            val offsetMap: Map<JsonNode, JsonNode> =
                stateNode
                    .properties()
                    .asSequence()
                    .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
                    .toMap()
            return DebeziumOffset(offsetMap)
        }

        internal fun position(offset: DebeziumOffset): PostgresSourceCdcPosition {
            check(offset.wrapped.size == 1) { "Debezium offset has unrecognized format" }
            val value = offset.wrapped.values.first()
            val lsn = value[LSN]?.asLong()
            val lsnCommit = value[LSN_COMMIT]?.asLong()
            return PostgresSourceCdcPosition(
                lsn = Lsn.valueOf(lsn),
                lsnCommit = Lsn.valueOf(lsnCommit),
            )
        }
    }

    val commonPropertiesBuilder by lazy {
        val tunnelSession: TunnelSession = connectionFactory.ensureTunnelSession()
        DebeziumPropertiesBuilder()
            .withDefault()
            // TODO: could be moved to withDefault()? Seems all connectors need this...
            .withOffset()
            .withConnector(PostgresConnector::class.java)
            .withDebeziumName(config.database)
            .withHeartbeats(config.debeziumHeartbeatInterval)
            .withDatabase(config.jdbcProperties)
            .withDatabase("hostname", tunnelSession.address.hostName)
            .withDatabase("port", tunnelSession.address.port.toString())
            .withDatabase("dbname", config.database)
            .with("snapshot.mode", "initial")
            .with("publication.autocreate.mode", "disabled")
            .with("converters", "datetime")
            .with("datetime.type", PostgresCustomConverter::class.java.name)
            .with("include.unknown.datatypes", "true")
            // TODO: This will eventually be deprecated in favor of lsn.flush.mode
            .with("flush.lsn.source", cdcConfig.debeziumCommitsLsn.toString())
            .with("plugin.name", "pgoutput")
            .with("slot.name", cdcConfig.replicationSlot)
            .with("publication.name", cdcConfig.publication)
            .apply {
                if (cdcConfig.heartbeatActionQuery?.isNotEmpty() ?: false) {
                    this.with("heartbeat.action.query", cdcConfig.heartbeatActionQuery!!)
                }
            }
            .withHeartbeatTimeout(cdcConfig.airbyteHeartbeatTimeout)
    }

    override fun startup(offset: DebeziumOffset) {
        // Need to validate replication slot even on cold start.
        // Debezium will retry in a loop if its invalid.
        // TODO: Honor configured InvalidCdcCursorPositionBehavior
        //  https://github.com/airbytehq/airbyte-internal-issues/issues/15680
        validate(offset)
        advanceReplicationSlot(offset)
    }

    override fun position(offset: DebeziumOffset): PostgresSourceCdcPosition {
        return Companion.position(offset)
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        val startup: StartupState =
            checkNotNull(this.startupState) {
                "StartupState bean is required for CDC but was not instantiated"
            }
        val key =
            Jsons.arrayNode()
                .add(config.database)
                .add(Jsons.objectNode().put(SERVER, config.database))
        val value =
            Jsons.objectNode()
                .putNull("transaction_id")
                .put(LSN, startup.lsn)
                .put(LSN_PROC, startup.lsn)
                // Postgres commits get their own LSNs, just like row-level changes. There is no way
                // of fetching the LSN of the latest commit, only the latest LSN overall. By putting
                // the max LSN into this field, we are telling Debezium that we've already seen and
                // processed all transactions before this LSN, which is true, as our snapshot will
                // include all transactions committed before this LSN. We will start streaming from
                // the next transaction greater than this LSN.
                .put(LSN_COMMIT, startup.lsn)
                .put("txId", startup.txId)
                .put("ts_usec", Conversions.toEpochMicros(startup.time))
        val wrapped = mapOf<JsonNode, JsonNode>(key to value)
        log.info { "Initial Debezium state constructed: $wrapped" }
        return DebeziumOffset(wrapped)
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
        commonPropertiesBuilder.withStreams(streams).buildMap()

    override fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState {
        val debeziumOffset: DebeziumOffset =
            try {
                deserializeStateUnvalidated(opaqueStateValue)
            } catch (e: Exception) {
                log.error(e) { "Error deserializing incumbent state value." }
                return AbortDebeziumWarmStartState(
                    "Error deserializing incumbent state value: ${e.message}"
                )
            }
        return ValidDebeziumWarmStartState(debeziumOffset, null)
    }

    // Commit the minimum of lsn_proc and lsn_commit to the replication slot
    private fun advanceReplicationSlot(offset: DebeziumOffset) {
        if (cdcConfig.debeziumCommitsLsn) return
        check(offset.wrapped.size == 1) { "Debezium offset has unrecognized format" }
        val value = offset.wrapped.values.first()
        val lsnProc = Lsn.valueOf(value[LSN_PROC]?.asLong())
        val lsnCommit = Lsn.valueOf(value[LSN_COMMIT]?.asLong())
        val lsnToAdvanceTo = listOfNotNull(lsnProc, lsnCommit).minOrNull() ?: return
        replicationSlotManager.advanceLsn(lsnToAdvanceTo)
    }

    private fun validate(offset: DebeziumOffset) {
        val lsn =
            position(offset).lsn
                ?: throw IllegalArgumentException("Offset does not contain LSN: $offset")
        replicationSlotManager.validate(lsn)
    }

    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
        commonPropertiesBuilder.withStreams(streams).buildMap()

    @Suppress("UNCHECKED_CAST")
    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream
    ): DeserializedRecord {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull

        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
        val resultRow: NativeRecordPayload = mutableMapOf()
        val changes = mutableMapOf<EmittedField, FieldValueChange>()
        for (field in stream.schema) {
            var mappedValue: JsonNode?
            if (field.type is ArrayFieldType<*>) {
                val rawArray = data[field.id]
                mappedValue =
                    if (rawArray == null || rawArray is NullNode) null
                    else {
                        Jsons.arrayNode().also { arr ->
                            (rawArray as ArrayNode).forEach {
                                val mappingResult =
                                    mapValue(it, (field.type as ArrayFieldType<*>).elementFieldType)
                                arr.add(mappingResult.getOrNull())
                                if (mappingResult.isFailure) {
                                    changes[EmittedField(field.id, field.type)] =
                                        FieldValueChange.DESERIALIZATION_FAILURE_PARTIAL
                                }
                            }
                        }
                    }
            } else {
                val mappingResult = mapValue(data[field.id], field.type)
                mappedValue = mappingResult.getOrNull()
                if (mappingResult.isFailure) {
                    changes[EmittedField(field.id, field.type)] =
                        FieldValueChange.DESERIALIZATION_FAILURE_TOTAL
                }
            }

            if (mappedValue != null) {
                when (mappedValue) {
                    is NullNode -> {
                        resultRow[field.id] = FieldValueEncoder(null, NullCodec)
                    }
                    else -> {
                        if (field.type is ArrayFieldType<*>) {
                            // ArrayEncoder needs a List<T>; decode the JSON array using the
                            // element type's decoder before passing to the encoder.
                            val elementDecoder =
                                (field.type as ArrayFieldType<*>).elementFieldType.jsonEncoder
                                    as JsonDecoder<Any?>
                            val arrayDecoder = ArrayDecoder(elementDecoder)
                            var decoded: List<Any?>? = null
                            try {
                                decoded = arrayDecoder.decode(mappedValue)
                            } catch (_: Exception) {
                                changes[EmittedField(field.id, field.type)] =
                                    FieldValueChange.DESERIALIZATION_FAILURE_TOTAL
                            }
                            resultRow[field.id] =
                                FieldValueEncoder(
                                    decoded,
                                    field.type.jsonEncoder as JsonEncoder<Any?>
                                )
                        } else {
                            val decoder = field.type.jsonEncoder as JsonDecoder<Any?>
                            var decoded: Any? = null
                            try {
                                decoded = decoder.decode(mappedValue)
                            } catch (_: Exception) {
                                changes[EmittedField(field.id, field.type)] =
                                    FieldValueChange.DESERIALIZATION_FAILURE_TOTAL
                            }
                            resultRow[field.id] =
                                FieldValueEncoder(
                                    decoded,
                                    decoder as JsonEncoder<Any?>,
                                )
                        }
                    }
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
                CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder as JsonEncoder<Any>,
            )
        resultRow[CommonMetaField.CDC_DELETED_AT.id] =
            FieldValueEncoder(
                if (isDelete) transactionOffsetDateTime else null,
                (if (isDelete) CommonMetaField.CDC_DELETED_AT.type.jsonEncoder else NullCodec)
                    as JsonEncoder<Any>,
            )
        resultRow[PostgresSourceCdcMetaFields.CDC_LSN.id] =
            FieldValueEncoder(
                // Legacy Airbyte type is Number but values are all Long. Here we convert.
                source[LSN].asLong().toBigDecimal(),
                PostgresSourceCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>,
            )

        // Return a DeserializedRecord instance.
        return DeserializedRecord(resultRow, changes)
    }

    // Json types and values from Debezium differ from those arriving via JDBC, which is what our
    // type system was designed to read. Here we map Debezium-flavored json values to JDBC-flavored
    // ones. This repeated conversion incurs a performance penalty. The efficient way would be to
    // inject our preferred serialization logic into Debezium directly.
    private fun mapValue(input: JsonNode?, fieldType: FieldType): Result<JsonNode?> {
        if (input == null || input is NullNode) return Result.success(input)
        try {
            val mappedValue =
                when (fieldType) {
                    FloatFieldType -> Jsons.numberNode(input.floatValue())
                    DoubleFieldType -> Jsons.numberNode(input.asDouble())
                    BigDecimalFieldType -> {
                        if (input.isNumber) input
                        else Jsons.numberNode(BigDecimal(input.textValue()).stripTrailingZeros())
                    }
                    BigIntegerFieldType -> {
                        if (input.isNumber && input.canConvertToExactIntegral()) input
                        else Jsons.numberNode(BigDecimal(input.textValue()))
                    }
                    // Debezium may emit non-textual nodes for columns that map to StringFieldType
                    StringFieldType ->
                        if (input.isTextual) input else Jsons.textNode(input.asText())
                    else -> input
                }
            return Result.success(mappedValue)
        } catch (e: Exception) {
            return Result.failure(e)
        }
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["schema"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue {
        // We want:
        // {
        //     "state": {
        //         "[\"postgres\",{\"server\":\"postgres\"}]":
        //              "{\"lsn_proc\":3575761602216,\"lsn\":3575761602216}"
        //     }
        // }
        val stateValueNode: ObjectNode =
            Jsons.objectNode().apply {
                for ((k, v) in offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        return Jsons.objectNode().apply { set<JsonNode>(STATE, stateValueNode) }
    }

    override fun position(recordValue: DebeziumRecordValue): PostgresSourceCdcPosition? {
        val source = recordValue.source
        val lsn = source[LSN]?.asLong()
        val sequence =
            Jsons.readValue(
                source["sequence"].toString(),
                object : TypeReference<List<String>>() {}
            )
        val lsnCommit = sequence?.get(0)?.toLong()
        return PostgresSourceCdcPosition(
            lsn = Lsn.valueOf(lsn),
            lsnCommit = Lsn.valueOf(lsnCommit),
        )
    }

    override fun position(sourceRecord: SourceRecord): PostgresSourceCdcPosition? {
        val lsn = sourceRecord.sourceOffset()[LSN] as Long?
        val lsnCommit = sourceRecord.sourceOffset()[LSN_COMMIT] as Long?
        return PostgresSourceCdcPosition(Lsn.valueOf(lsn), Lsn.valueOf(lsnCommit))
    }
}
