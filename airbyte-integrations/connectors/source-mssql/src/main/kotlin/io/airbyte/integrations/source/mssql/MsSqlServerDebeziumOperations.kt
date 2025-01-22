/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.*
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.sqlserver.Lsn
import io.debezium.connector.sqlserver.SqlServerConnector
import io.debezium.connector.sqlserver.TxLogPosition
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.debezium.relational.history.SchemaHistory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.kafka.connect.source.SourceRecord
import org.apache.mina.util.Base64
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Duration
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream

private val log = KotlinLogging.logger {}
@Singleton
class MsSqlServerDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: MsSqlServerSourceConfiguration,
) : DebeziumOperations<TxLogPosition> {
    val recordCounter = AtomicLong(Instant.now().toEpochMilli()*100_00_000 + 1)
    override fun position(offset: DebeziumOffset): TxLogPosition {
        if (offset.wrapped.size != 1) {
            throw ConfigErrorException("Expected exactly 1 key in $offset")
        }
        val offsetValue: ObjectNode = offset.wrapped.values.first() as ObjectNode
        val commitLsn: String = offsetValue["commit_lsn"].asText()
        val changeLsn: String? = null//offsetValue["change_lsn"].asText()
        val commitLsn2: String = offsetValue["commit_lsn"].asText()
        val changeLsn2: String? = null//offsetValue["change_lsn"].asText()
        val retVal = TxLogPosition.valueOf(Lsn.valueOf(commitLsn), Lsn.valueOf(changeLsn))
        log.info { "SGX offsetValue = $offsetValue, commitLsn=$commitLsn, changeLsn=$changeLsn, commitLsn2=$commitLsn2, changeLsn2=$changeLsn2, retVal=$retVal" }
        return retVal
    }

    override fun position(recordValue: DebeziumRecordValue): TxLogPosition? {
        val commitLsn: String =
            recordValue.source["commit_lsn"]?.takeIf { it.isTextual }?.asText() ?: return null
        val changeLsn: String? = null
            //recordValue.source["change_lsn"]?.takeIf { it.isTextual }?.asText()
        log.info { "SGX recordValue.source = ${recordValue.source}" }
        return TxLogPosition.valueOf(Lsn.valueOf(commitLsn), Lsn.valueOf(changeLsn))
    }

    override fun position(sourceRecord: SourceRecord): TxLogPosition? {
        val commitLsn: String = sourceRecord.sourceOffset()[("commit_lsn")]?.toString() ?: return null
        val changeLsn: String? = null//sourceRecord.sourceOffset()[("change_lsn")]?.toString()
        log.info { "SGX sourceRecord.sourceOffset() = ${sourceRecord.sourceOffset()}" }
        return TxLogPosition.valueOf(Lsn.valueOf(commitLsn), Lsn.valueOf(changeLsn))
    }

    override fun synthesize(): DebeziumInput {
        val lsn = queryMaxLsn()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply {
                    put("server", databaseName)
                    put("database", databaseName)
                })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("commit_lsn", lsn.toString())
                //put("change_lsn", lsn.toString())
                put("snapshot", true)
                put("snapshot_completed", true)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        val state = DebeziumState(offset, schemaHistory = DebeziumSchemaHistory(emptyList()))

        log.info { "SGX returning real state: $state" }
        return DebeziumInput(
            commonProperties() + ("snapshot.mode" to "recovery"),
            state,
            isSynthetic = true
        )
    }

    override fun deserialize(
        opaqueStateValue: OpaqueStateValue,
        streams: List<Stream>
    ): DebeziumInput {
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
        val schemaHistory: DebeziumSchemaHistory? = historyNode?.let {
            val isCompressed: Boolean = stateNode[MSSQL_IS_COMPRESSED]?.asBoolean() ?: false
            val uncompressedString: String =
                if (isCompressed) {
                    val textValue: String = it.textValue()
                    val compressedBytes: ByteArray =
                        textValue.substring(1, textValue.length - 1).toByteArray(Charsets.UTF_8)
                    val decoded = Base64.decodeBase64(compressedBytes)

                    GZIPInputStream(ByteArrayInputStream(decoded)).reader(Charsets.UTF_8).readText()
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

        return DebeziumInput(
            isSynthetic = false,
            state = DebeziumState(offset, schemaHistory),
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
            properties = commonProperties() + ("snapshot.mode" to "when_needed")
        )
    }

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord? {
        log.info{"SGX deserializing debezium record $value for key $key"}
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull
        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
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
        val commitLsn = source["commit_lsn"].asText()
        data.set<JsonNode>(MsSqlServerCdcMetaFields.CDC_LSN.id, TextCodec.encode(commitLsn))
        // Set the _ab_cdc_cursor meta-field value.
        data.set<JsonNode>(MsSqlServerCdcMetaFields.CDC_CURSOR.id, LongCodec.encode(recordCounter.getAndIncrement()))
        // Return a DeserializedRecord instance.
        return DeserializedRecord(data, changes = emptyMap())
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        val retVal = value.source["schema"]?.asText()
        log.info {"SGX returning $retVal. key=$key, value=$value"}
        return retVal
    }

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? {
        val retVal = value.source["table"]?.asText()
        log.info {"SGX returning $retVal. key=$key, value=$value"}
        return retVal
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
        stateNode.set<JsonNode>(MSSQL_CDC_OFFSET, offsetNode)

        val schemaHistory: List<HistoryRecord>? = debeziumState.schemaHistory?.wrapped
        if (schemaHistory != null) {
            val uncompressedString: String =
                schemaHistory.joinToString(separator = "\n") {
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

    val databaseName: String = configuration.databaseName

    private fun queryMaxLsn(): Lsn {
        val maxLsn = Field("max_lsn", BytesFieldType)
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "select sys.fn_cdc_get_max_lsn() as max_lsn"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    return Lsn.valueOf(rs.getBytes(maxLsn.id))
                }
            }
        }
    }

    enum class MsSqlServerCdcMetaFields(
        override val type: FieldType,
    ) : MetaField {
        CDC_CURSOR(CdcIntegerMetaFieldType),
        CDC_LSN(CdcStringMetaFieldType),
        ;

        override val id: String
            get() = MetaField.META_PREFIX + name.lowercase()
    }

    private fun commonProperties(): Map<String, String> {
        val tunnelSession = jdbcConnectionFactory.ensureTunnelSession()
        return DebeziumPropertiesBuilder()
            .with(staticProperties)

            .withDebeziumName(databaseName)
            .withHeartbeats(Duration.ofSeconds(1))
            //TODO: should be a join of all the schemas across streams.
            .with("schema.include.list", configuration.namespaces.joinToString(","))
            .with("database.names", databaseName)

            .withDatabase(configuration.jdbcProperties)
            .withDatabase("hostname", tunnelSession.address.hostName)
            .withDatabase("port", tunnelSession.address.port.toString())
            .withDatabase("dbname", databaseName)
            .buildMap()
    }

    companion object {
        const val MSSQL_MAX_UNCOMPRESSED_LENGTH = 1024 * 1024
        const val MSSQL_STATE = "state"
        const val MSSQL_CDC_OFFSET = "mssql_cdc_offset"
        const val MSSQL_DB_HISTORY = "mssql_db_history"
        const val MSSQL_IS_COMPRESSED = "is_compressed"
        init {
            File("/tmp/sgx_schema_history").mkdirs()
        }

        val staticProperties: Map<String, String> =
                DebeziumPropertiesBuilder()
                    .withDefault()
                    .withConnector(SqlServerConnector::class.java)
                    // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-include-schema-changes
                    .with("include.schema.changes", "false")
                    // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
                    .with("provide.transaction.metadata", "false")
                    // This to make sure that binary data represented as a base64-encoded String.
                    // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
                    .with("binary.handling.mode", "base64")
                    // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-locking-mode
                    // This is to make sure other database clients are allowed to write to a table while
                    // Airbyte is taking a snapshot. There is a risk involved that if any database
                    // client
                    // makes a schema change then the sync might break
                    .with("snapshot.locking.mode", "none")
                    //SGX: ??
                    .with("mssql_converter.type", MsSqlServerDebeziumConverter::class.java.getName())
                    .with("converters", "mssql_converter")
                    .with("snapshot.isolation.mode", "read_committed")

                    // 10 sec in prod. Should be 1s in test...
                    .withHeartbeats(Duration.ofSeconds(10))
                    .withOffset()
                    .withSchemaHistory()
                    .buildMap()


    }
}

class MsSqlServerDebeziumPosition : Comparable<MsSqlServerDebeziumPosition> {
    override fun compareTo(other: MsSqlServerDebeziumPosition): Int {
        log.info{"SGX returning 0!!! other=$other, this=$this"}
        return 0
    }
}
