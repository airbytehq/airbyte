/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import com.fasterxml.jackson.core.type.TypeReference
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.NullCodec
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
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumWarmStartState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.PostgresConnector
import io.debezium.connector.postgresql.connection.Lsn
import io.debezium.time.Conversions
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import kotlin.collections.component1
import kotlin.collections.component2
import org.apache.kafka.connect.source.SourceRecord

@Singleton
class PostgresSourceDebeziumOperations(val config: PostgresSourceConfiguration) :
    CdcPartitionsCreatorDebeziumOperations<PostgresSourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<PostgresSourceCdcPosition> {

    private val log = KotlinLogging.logger {}

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
                    .fields()
                    .asSequence()
                    .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
                    .toMap()
            return DebeziumOffset(offsetMap)
        }

        internal fun position(offset: DebeziumOffset): PostgresSourceCdcPosition {
            check(offset.wrapped.size == 1) { "Debezium offset has unrecognized format" }
            val value = offset.wrapped.values.first()
            val lsn = value[LSN]?.asLong()
            return PostgresSourceCdcPosition(
                lsn = Lsn.valueOf(lsn),
                lsnCommit = null, // not present in state
            )
        }
    }

    val cdcConfig by lazy { config.cdc!! }

    val commonPropertiesBuilder by lazy {
        DebeziumPropertiesBuilder()
            .withDefault()
            // TODO: could be moved to withDefault()? Seems all connectors need this...
            .withOffset()
            .withConnector(PostgresConnector::class.java)
            .withDebeziumName(config.database)
            .withHeartbeats(config.debeziumHeartbeatInterval)
            .withDatabase(config.jdbcProperties)
            .withDatabase("hostname", config.realHost)
            .withDatabase("port", config.realPort.toString())
            .withDatabase("dbname", config.database)
            .with("snapshot.mode", "initial")
            .with("publication.autocreate.mode", "disabled")
            .with("converters", "datetime")
            .with("datetime.type", PostgresDebeziumDatetimeConverter::class.java.name)
            .with("include.unknown.datatypes", "true")
            .with("flush.lsn.source", cdcConfig.debeziumCommitsLsn.toString())
            .with("plugin.name", "pgoutput")
            .with("slot.name", cdcConfig.replicationSlot)
            .with("publication.name", cdcConfig.publication)
        // TODO: heartbeat.action.query
        // TODO: SSL support
    }

    // Ensure these are fetched only once for correctness.
    // This class is a @Singleton and "lazy" is synchronized.
    val startupState: StartupState by lazy {
        val txId: Long
        val lsn: Long
        // TODO: Take timestamp from DB, not application
        val time: Instant = Instant.now()
        JdbcConnectionFactory(config).get().use { connection ->
            connection.createStatement().use {
                it.execute(
                    "SELECT CASE WHEN pg_is_in_recovery() THEN txid_snapshot_xmin(txid_current_snapshot()) ELSE txid_current() END AS pg_current_txid;"
                )
                check(it.resultSet.next()) { "Query for txid produced no results" }
                check(it.resultSet.isLast) { "Query for txid produced more than one result" }
                txId = it.resultSet!!.getLong(1)
            }
            connection.createStatement().use {
                // pg version >= 10. For versions < 10 use query select * from
                // pg_current_xlog_location()
                it.execute(
                    "SELECT CASE WHEN pg_is_in_recovery() THEN pg_last_wal_receive_lsn() ELSE pg_current_wal_lsn() END AS pg_current_wal_lsn;"
                )
                check(it.resultSet.next()) { "Query for lsn produced no results" }
                check(it.resultSet.isLast) { "Query for lsn produced more than one result" }
                lsn = Lsn.valueOf(it.resultSet!!.getString(1)).asLong()
            }
        }
        StartupState(txId, lsn, time)
    }

    data class StartupState(val txId: Long, val lsn: Long, val time: Instant = Instant.now())

    override fun position(offset: DebeziumOffset): PostgresSourceCdcPosition {
        return Companion.position(offset)
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        val key =
            Jsons.arrayNode()
                .add(config.database)
                .add(Jsons.objectNode().put(SERVER, config.database))
        val value =
            Jsons.objectNode()
                .putNull("transaction_id")
                .put(LSN, startupState.lsn)
                .put(LSN_PROC, startupState.lsn)
                .put("txId", startupState.txId)
                .put("ts_usec", Conversions.toEpochMicros(startupState.time))
        val wrapped = mapOf<JsonNode, JsonNode>(key to value)
        log.info { "Initial Debezium state constructed: $wrapped" }
        return DebeziumOffset(wrapped)
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
        commonPropertiesBuilder.withStreams(streams).buildMap()

    override fun deserializeState(opaqueStateValue: OpaqueStateValue): DebeziumWarmStartState {
        val debeziumState: DebeziumOffset =
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

    private fun validate(offset: DebeziumOffset): DebeziumWarmStartState {
        // TODO: check that binlog position is available on replication slot
        return ValidDebeziumWarmStartState(offset, null)
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
        for (field in stream.schema) {
            data[field.id] ?: continue
            when (data[field.id]) {
                is NullNode -> {
                    resultRow[field.id] = FieldValueEncoder(null, NullCodec)
                }
                else -> {
                    val codec: JsonCodec<*> = field.type.jsonEncoder as JsonCodec<*>
                    @Suppress("UNCHECKED_CAST")
                    resultRow[field.id] =
                        FieldValueEncoder(
                            codec.decode(data[field.id]),
                            field.type.jsonEncoder as JsonCodec<Any>,
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
                source[LSN].asText(),
                PostgresSourceCdcMetaFields.CDC_LSN.type.jsonEncoder as JsonEncoder<Any>,
            )

        // Return a DeserializedRecord instance.
        return DeserializedRecord(resultRow, emptyMap())
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
