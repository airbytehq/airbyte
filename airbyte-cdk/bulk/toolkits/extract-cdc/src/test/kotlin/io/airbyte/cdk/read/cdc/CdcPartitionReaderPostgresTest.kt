package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.postgresql.PostgresConnector
import java.sql.Connection
import java.sql.Statement
import java.time.Instant
import org.apache.kafka.connect.source.SourceRecord
import org.postgresql.replication.LogSequenceNumber
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName

class CdcPartitionReaderPostgresTest :
    AbstractCdcPartitionReaderTest<LogSequenceNumber, PostgreSQLContainer<*>>(
        namespace = "public",
    ) {

    override fun createContainer(): PostgreSQLContainer<*> {
        val dockerImageName: DockerImageName =
            DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(DOCKER_IMAGE_NAME)
        val modifier: TestContainerFactory.ContainerModifier<PostgreSQLContainer<*>> =
            TestContainerFactory.newModifier("withWalLevelLogical") {
                it.withCommand("postgres -c wal_level=logical")
            }
        return TestContainerFactory.exclusive(dockerImageName, modifier)
    }

    companion object {
        const val DOCKER_IMAGE_NAME = "postgres:13-alpine"
        init {
            TestContainerFactory.register(DOCKER_IMAGE_NAME, ::PostgreSQLContainer)
        }
        const val PUBLICATION_NAME = "test_publication"
        const val SLOT_NAME = "test_slot"
    }

    override fun PostgreSQLContainer<*>.createStream() {
        withStatement { it.execute("CREATE TABLE tbl (id SERIAL PRIMARY KEY, v INT)") }
        withStatement { it.execute("ALTER TABLE tbl REPLICA IDENTITY FULL") }
        withStatement {
            it.execute("SELECT pg_create_logical_replication_slot('$SLOT_NAME', 'pgoutput')")
        }
        withStatement { it.execute("CREATE PUBLICATION $PUBLICATION_NAME FOR TABLE tbl") }
    }

    override fun PostgreSQLContainer<*>.insert12345() {
        for (i in 1..5) {
            withStatement { it.execute("INSERT INTO tbl (v) VALUES ($i)") }
        }
    }

    override fun PostgreSQLContainer<*>.update135() {
        withStatement { it.execute("UPDATE tbl SET v = 6 WHERE id = 1") }
        withStatement { it.execute("UPDATE tbl SET v = 7 WHERE id = 3") }
        withStatement { it.execute("UPDATE tbl SET v = 8 WHERE id = 5") }
    }

    override fun PostgreSQLContainer<*>.delete24() {
        withStatement { it.execute("DELETE FROM tbl WHERE id = 2") }
        withStatement { it.execute("DELETE FROM tbl WHERE id = 4") }
    }

    private fun <X> PostgreSQLContainer<*>.withStatement(fn: (Statement) -> X): X =
        createConnection("").use { connection: Connection ->
            connection.createStatement().use { fn(it) }
        }

    override fun position(recordValue: DebeziumRecordValue): LogSequenceNumber? {
        val lsn: Long =
            recordValue.source["lsn"]?.takeIf { it.isIntegralNumber }?.asLong() ?: return null
        return LogSequenceNumber.valueOf(lsn)
    }

    override fun position(sourceRecord: SourceRecord): LogSequenceNumber? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val lsn: Long = offset["lsn"] as? Long ?: return null
        return LogSequenceNumber.valueOf(lsn)
    }

    override fun PostgreSQLContainer<*>.currentPosition(): LogSequenceNumber =
        withStatement { statement: Statement ->
            statement.executeQuery("SELECT pg_current_wal_lsn()").use {
                it.next()
                LogSequenceNumber.valueOf(it.getString(1))
            }
        }

    override fun PostgreSQLContainer<*>.syntheticInput(): DebeziumInput {
        val (position: LogSequenceNumber, txID: Long) =
            withStatement { statement: Statement ->
                statement.executeQuery("SELECT pg_current_wal_lsn(), txid_current()").use {
                    it.next()
                    LogSequenceNumber.valueOf(it.getString(1)) to it.getLong(2)
                }
            }
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", databaseName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_usec", timestamp.toEpochMilli() * 1000L)
                put("lsn", position.asLong())
                put("txId", txID)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        val state = DebeziumState(offset, schemaHistory = null)
        val syntheticProperties: Map<String, String> = debeziumProperties()
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    override fun PostgreSQLContainer<*>.debeziumProperties(): Map<String, String> =
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(PostgresConnector::class.java)
            .withDebeziumName(databaseName)
            .withHeartbeats(heartbeat)
            .with("plugin.name", "pgoutput")
            .with("slot.name", SLOT_NAME)
            .with("publication.name", PUBLICATION_NAME)
            .with("publication.autocreate.mode", "disabled")
            .with("flush.lsn.source", "false")
            .withDatabase("hostname", host)
            .withDatabase("port", firstMappedPort.toString())
            .withDatabase("user", username)
            .withDatabase("password", password)
            .withDatabase("dbname", databaseName)
            .withOffset()
            .withStreams(listOf(stream))
            .buildMap()
}
