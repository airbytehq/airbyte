/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.BinaryNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumInput
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.oracle.OracleConnector
import io.debezium.connector.oracle.converters.NumberOneToBooleanConverter
import io.debezium.connector.oracle.converters.NumberToZeroScaleConverter
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.net.InetSocketAddress
import java.security.MessageDigest
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.Base64
import java.util.function.Supplier
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import org.apache.kafka.connect.source.SourceRecord

@Singleton
class OracleSourceDebeziumOperations(
    val configuration: OracleSourceConfiguration,
    val oracleDatabaseStateSupplier: Supplier<CurrentDatabaseState>,
) : DebeziumOperations<OracleSourcePosition> {

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord? {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        if (before.isNull && after.isNull) {
            return null
        }
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull
        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
        // Turn string representations of numbers into BigDecimals.
        for (field in stream.schema) {
            when (field.type.airbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER,
                LeafAirbyteSchemaType.NUMBER -> Unit
                else -> continue
            }
            val textNode: TextNode = data[field.id] as? TextNode ?: continue
            data.put(field.id, BigDecimal(textNode.textValue()).stripTrailingZeros())
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
        // Set _ab_cdc_scn meta-field value.
        val position = OracleSourcePosition(source["scn"].asLong())
        data.set<JsonNode>(
            OracleSourceCdcScn.id,
            CdcIntegerMetaFieldType.jsonEncoder.encode(position.scn),
        )
        // Return a DeserializedRecord instance.
        return DeserializedRecord(data, changes = emptyMap())
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["schema"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

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

        val properties =
            DebeziumPropertiesBuilder()
                .with(commonProperties)
                .with("snapshot.mode", "when_needed")
                .withStreams(streams)
                // Custom metric tags are required for smooth repeated DebeziumEngine
                // initialization, otherwise we get error messages due to name collisions
                // when debezium-oracle registers JMX metrics beans.
                .with("custom.metric.tags", customMetricTags(debeziumState))
                .buildMap()
        return DebeziumInput(properties, debeziumState, isSynthetic = false)
    }

    override fun position(offset: DebeziumOffset): OracleSourcePosition = Companion.position(offset)

    override fun position(recordValue: DebeziumRecordValue): OracleSourcePosition? =
        recordValue.source["scn"]?.asLong()?.let(::OracleSourcePosition)

    override fun position(sourceRecord: SourceRecord): OracleSourcePosition? =
        (sourceRecord.sourceOffset()["scn"])?.toString()?.toLong()?.let(::OracleSourcePosition)

    override fun serialize(debeziumState: DebeziumState): OpaqueStateValue {
        val result: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in debeziumState.offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        result.set<JsonNode>(OFFSET, offsetNode)
        // Serialize schema history.
        val schemaHistory: List<HistoryRecord> =
            debeziumState.schemaHistory?.wrapped ?: return result
        val uncompressed: ArrayNode =
            Jsons.arrayNode().apply {
                for (historyRecord in schemaHistory) {
                    add(DocumentWriter.defaultWriter().write(historyRecord.document()))
                }
            }
        val uncompressedBytes: ByteArray = Jsons.writeValueAsBytes(uncompressed)
        if (uncompressedBytes.size < COMPRESSION_THRESHOLD) {
            result.set<JsonNode>(SCHEMA_HISTORY, uncompressed)
            return result
        }
        val baos = ByteArrayOutputStream()
        GZIPOutputStream(baos).use { it.write(uncompressedBytes) }
        result.put(SCHEMA_HISTORY, baos.toByteArray())
        return result
    }

    override fun synthesize(): DebeziumInput {
        val properties =
            DebeziumPropertiesBuilder()
                .with(commonProperties)
                // See comment in [deserialize] for why we're setting a custom metric tag here.
                .with("custom.metric.tags", "synthetic=true")
                .with("snapshot.mode", "recovery")
                // This extra exclude list is required to support Amazon RDS.
                // Otherwise, Debezium tries to lock tables in the ADMIN and RDSADMIN schemas
                // when capturing the schema change history of the database.
                // For some reason, these tables are not present in the hardcoded ignore-list:
                // https://debezium.io/documentation/reference/stable/connectors/oracle.html#schemas-that-the-debezium-oracle-connector-excludes-when-capturing-change-events
                .with("table.exclude.list", """"?RDSADMIN"?\..*,"?ADMIN"?\..*""")
                .buildMap()
        val offsetKey: JsonNode =
            Jsons.arrayNode().apply {
                add(currentDatabaseState.debeziumName)
                add(Jsons.objectNode().apply { put("server", currentDatabaseState.debeziumName) })
            }
        val offsetValue: JsonNode =
            Jsons.objectNode().apply {
                putNull("commit_scn")
                putNull("snapshot_scn")
                put("scn", currentDatabaseState.position.scn)
            }
        val offset = DebeziumOffset(mapOf(offsetKey to offsetValue))
        val state = DebeziumState(offset, DebeziumSchemaHistory(emptyList()))
        return DebeziumInput(properties, state, isSynthetic = true)
    }

    private val currentDatabaseState: CurrentDatabaseState by lazy {
        oracleDatabaseStateSupplier.get()
    }

    @Singleton
    class OracleDatabaseStateSupplier(val jdbcConnectionFactory: JdbcConnectionFactory) :
        Supplier<CurrentDatabaseState> {

        override fun get(): CurrentDatabaseState =
            jdbcConnectionFactory.get().use { connection: Connection ->
                connection.createStatement().use { statement: Statement ->
                    statement.executeQuery(CurrentDatabaseState.SQL).use { rs: ResultSet ->
                        require(rs.next())
                        val isContainerDatabase: Boolean = rs.getString(1)?.uppercase() == "YES"
                        val pluggableDatabaseName: String? =
                            if (isContainerDatabase) rs.getString(2) else null
                        CurrentDatabaseState(
                            address = jdbcConnectionFactory.ensureTunnelSession().address,
                            pluggableDatabaseName,
                            databaseName = rs.getString(3)!!,
                            position = OracleSourcePosition(rs.getLong(4)),
                        )
                    }
                }
            }
    }

    data class CurrentDatabaseState(
        val address: InetSocketAddress,
        val pluggableDatabaseName: String?,
        val databaseName: String,
        val position: OracleSourcePosition,
    ) {
        val debeziumName: String
            get() = pluggableDatabaseName ?: databaseName

        companion object {
            const val SQL =
                """
    SELECT
        cdb,
        SYS_CONTEXT('USERENV', 'CON_NAME') AS pdb_name,
        name AS db_name,
        current_scn
    FROM v${'$'}database
            """
        }
    }

    val commonProperties: Map<String, String> by lazy {
        val address: InetSocketAddress = currentDatabaseState.address
        DebeziumPropertiesBuilder()
            .withDefault()
            .withOffset()
            .withSchemaHistory()
            .withDebeziumName(currentDatabaseState.debeziumName)
            .withConnector(OracleConnector::class.java)
            .withHeartbeats(configuration.debeziumHeartbeatInterval)
            .withDatabase(configuration.jdbcProperties)
            .withDatabase("hostname", address.hostName)
            .withDatabase("port", address.port.toString())
            .withDatabase("dbname", currentDatabaseState.databaseName)
            .also {
                val pdbName: String = currentDatabaseState.pluggableDatabaseName ?: return@also
                it.withDatabase("pdb.name", pdbName)
            }
            .with("schema.history.internal.store.only.captured.databases.ddl", "true")
            .with("converters", "$CONVERTER_KEY,zero_scale,boolean")
            .with("$CONVERTER_KEY.type", OracleAirbyteCustomConverter::class.qualifiedName!!)
            .with("zero_scale.type", NumberToZeroScaleConverter::class.qualifiedName!!)
            .with("boolean.type", NumberOneToBooleanConverter::class.qualifiedName!!)
            .with(
                "debezium.embedded.shutdown.pause.before.interrupt.ms",
                configuration.cdc!!.shutdownTimeout.toMillis().toString(),
            )
            .buildMap()
    }

    companion object {
        const val COMPRESSION_THRESHOLD = 1_000_000
        const val OFFSET = "offset"
        const val SCHEMA_HISTORY = "schema_history"
        const val CONVERTER_KEY = "oracle-airbyte-custom-converter"

        internal fun position(offset: DebeziumOffset): OracleSourcePosition =
            OracleSourcePosition(offset.wrapped.values.firstOrNull()?.get("scn")?.asLong() ?: 0)

        internal fun deserializeDebeziumState(opaqueStateValue: OpaqueStateValue): DebeziumState {
            // Deserialize offset.
            val offsetNode: ObjectNode = opaqueStateValue[OFFSET] as ObjectNode
            val offsetMap: Map<JsonNode, JsonNode> =
                offsetNode
                    .fields()
                    .asSequence()
                    .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
                    .toMap()
            if (offsetMap.size != 1) {
                throw RuntimeException("$OFFSET object should have 1 key in $opaqueStateValue")
            }
            val offset = DebeziumOffset(offsetMap)
            // Deserialize schema history.
            val uncompressedSchemaHistoryNode: ArrayNode =
                when (val node: JsonNode? = opaqueStateValue[SCHEMA_HISTORY]) {
                    is ArrayNode -> node
                    is NullNode,
                    null -> return DebeziumState(offset, schemaHistory = null)
                    is BinaryNode -> unzipSchemaHistory(node.binaryValue())
                    is TextNode -> unzipSchemaHistory(node.textValue())
                    else -> throw ConfigErrorException("unexpected type for $SCHEMA_HISTORY")
                }
            val decodedRecords: List<HistoryRecord> =
                uncompressedSchemaHistoryNode
                    .elements()
                    .asSequence()
                    .map { HistoryRecord(DocumentReader.defaultReader().read(it.asText())) }
                    .toList()
            return DebeziumState(offset, DebeziumSchemaHistory(decodedRecords))
        }

        private fun unzipSchemaHistory(gzippedSchemaHistoryBase64: String): ArrayNode =
            unzipSchemaHistory(Base64.getDecoder().decode(gzippedSchemaHistoryBase64))

        private fun unzipSchemaHistory(gzippedSchemaHistory: ByteArray): ArrayNode {
            val unzipped: ByteArray =
                GZIPInputStream(ByteArrayInputStream(gzippedSchemaHistory)).readAllBytes()
            return Jsons.readTree(unzipped) as ArrayNode
        }

        internal fun customMetricTags(debeziumState: DebeziumState): String {
            val position: OracleSourcePosition = position(debeziumState.offset)
            val offsetBytes: ByteArray =
                debeziumState.offset.wrapped.toString().toByteArray(Charsets.UTF_8)
            val hashBytes: ByteArray = MessageDigest.getInstance("MD5").digest(offsetBytes)
            val hashString: String = Base64.getEncoder().encodeToString(hashBytes)
            return "initial_scn=${position.scn},initial_offset_hash=$hashString"
        }
    }
}
