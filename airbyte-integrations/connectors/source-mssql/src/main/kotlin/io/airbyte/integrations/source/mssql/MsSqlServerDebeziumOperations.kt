/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
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
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.kafka.connect.source.SourceRecord
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import java.time.Duration
import java.time.Instant
import java.util.*

@Singleton
class MsSqlServerDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: MsSqlServerSourceConfiguration,
) : DebeziumOperations<MsSqlServerDebeziumPosition> {
    override fun position(offset: DebeziumOffset): MsSqlServerDebeziumPosition {
        log.info {"SGX returning empty MsSqlServerDebeziumPosition"}
        return MsSqlServerDebeziumPosition()
    }

    override fun position(recordValue: DebeziumRecordValue): MsSqlServerDebeziumPosition? {
        log.info {"SGX returning empty MsSqlServerDebeziumPosition"}
        return MsSqlServerDebeziumPosition()
    }

    override fun position(sourceRecord: SourceRecord): MsSqlServerDebeziumPosition? {
        log.info {"SGX returning empty MsSqlServerDebeziumPosition"}
        return MsSqlServerDebeziumPosition()
    }

    override fun synthesize(): DebeziumInput {
        val lsn = queryMaxLsn()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply {
                    put("server", databaseName)
                    put("dbName", databaseName)
                })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("commit_lsn", lsn.toString())
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        val state = DebeziumState(offset, schemaHistory = null)

        log.info { "SGX returning real state: $state" }
        return DebeziumInput(DebeziumPropertiesBuilder()
            .with(commonProperties)
            // If not in snapshot mode, initial will make sure that a snapshot is taken if the transaction log
            // is rotated out. This will also end up read streaming changes from the transaction_log.
            .with("snapshot.mode", "when_needed")
            .withStreams(listOf())
            .buildMap(), state, isSynthetic = true)
    }

    override fun deserialize(
        opaqueStateValue: OpaqueStateValue,
        streams: List<Stream>
    ): DebeziumInput {
        log.info {"SGX returning dummy"}
        return DebeziumInput(
            isSynthetic = true,
            state = DebeziumState(DebeziumOffset(emptyMap()), null),
            properties = emptyMap()
        )
    }

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord? {
        log.info {"SGX returning dummy"}
        return null
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
        log.info {"SGX returniong empty node"}
        return Jsons.objectNode()
    }

    val databaseName: String = configuration.databaseName
    val commonProperties: Map<String, String> by lazy {
        val tunnelSession: TunnelSession = jdbcConnectionFactory.ensureTunnelSession()
        val dbzPropertiesBuilder =
            DebeziumPropertiesBuilder()
                .withDefault()
                .withConnector(SqlServerConnector::class.java)
                // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-include-schema-changes
                .with("include.schema.changes", "false")
                // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
                .with("provide.transaction.metadata", "false")

                .withDebeziumName(databaseName)
                .withHeartbeats(configuration.debeziumHeartbeatInterval)
                // This to make sure that binary data represented as a base64-encoded String.
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
                .with("binary.handling.mode", "base64")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
                .with("snapshot.mode", "when_needed")
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
                //TODO: should be a join of all the schemas across streams.
                .with("schema.include.list", configuration.namespaces.joinToString(","))
                .with("database.names", databaseName)

                // 10 sec in ms. Should be 1s in test...
                .withHeartbeats(Duration.ofSeconds(10))

                .withDatabase(configuration.jdbcProperties)
                .withDatabase("hostname", tunnelSession.address.hostName)
                .withDatabase("port", tunnelSession.address.port.toString())
                .withDatabase("dbname", databaseName)
                .withOffset()
                .withSchemaHistory()


        // If new stream(s) are added after a previously successful sync,
        // the snapshot.mode needs to be initial_only since we don't want to continue streaming changes
        // https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#sqlserver-property-snapshot-mode
        /*if (isSnapshot) {
            props.setProperty("snapshot.mode", "initial_only")
        } else {
            // If not in snapshot mode, initial will make sure that a snapshot is taken if the transaction log
            // is rotated out. This will also end up read streaming changes from the transaction_log.
            props.setProperty("snapshot.mode", "when_needed")
        }*/
        dbzPropertiesBuilder.buildMap()
    }

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

    companion object {
        private val log = KotlinLogging.logger {}
    }
}

class MsSqlServerDebeziumPosition : Comparable<MsSqlServerDebeziumPosition> {
    override fun compareTo(other: MsSqlServerDebeziumPosition): Int {
        return 0
    }
}
