/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.MySqlConnector
import java.sql.Connection
import java.sql.Statement
import java.time.Instant
import kotlin.random.Random
import kotlin.random.nextInt
import org.apache.kafka.connect.source.SourceRecord
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.utility.DockerImageName

class CdcPartitionReaderMySQLTest :
    AbstractCdcPartitionReaderTest<CdcPartitionReaderMySQLTest.Position, MySQLContainer<*>>(
        namespace = "test",
    ) {

    data class Position(val file: String, val pos: Long) : Comparable<Position> {
        override fun compareTo(other: Position): Int =
            file.compareTo(other.file).takeUnless { it == 0 } ?: pos.compareTo(other.pos)
    }

    override fun createContainer(): MySQLContainer<*> {
        val dockerImageName: DockerImageName =
            DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(DOCKER_IMAGE_NAME)
        val modifier: TestContainerFactory.ContainerModifier<MySQLContainer<*>> =
            TestContainerFactory.newModifier("withRoot") { it.withUsername("root") }
        return TestContainerFactory.exclusive(dockerImageName, modifier)
    }

    companion object {
        const val DOCKER_IMAGE_NAME = "mysql:8.0"
        init {
            TestContainerFactory.register(DOCKER_IMAGE_NAME, ::MySQLContainer)
        }
    }

    override fun MySQLContainer<*>.createStream() {
        withStatement { it.execute("CREATE TABLE tbl (id INT AUTO_INCREMENT PRIMARY KEY, v INT)") }
    }

    override fun MySQLContainer<*>.insert12345() {
        for (i in 1..5) {
            withStatement { it.execute("INSERT INTO tbl (v) VALUES ($i)") }
        }
    }

    override fun MySQLContainer<*>.update135() {
        withStatement { it.execute("UPDATE tbl SET v = 6 WHERE id = 1") }
        withStatement { it.execute("UPDATE tbl SET v = 7 WHERE id = 3") }
        withStatement { it.execute("UPDATE tbl SET v = 8 WHERE id = 5") }
    }

    override fun MySQLContainer<*>.delete24() {
        withStatement { it.execute("DELETE FROM tbl WHERE id = 2") }
        withStatement { it.execute("DELETE FROM tbl WHERE id = 4") }
    }

    private fun <X> MySQLContainer<*>.withStatement(fn: (Statement) -> X): X =
        createConnection("").use { connection: Connection ->
            connection.createStatement().use { fn(it) }
        }

    override fun createDebeziumOperations(): DebeziumOperations<Position> =
        MySQLTestDebeziumOperations()

    inner class MySQLTestDebeziumOperations : AbstractDebeziumOperationsForTest<Position>() {

        override fun position(offset: DebeziumOffset): Position {
            val offsetAsJson = offset.wrapped.values.first()
            val retVal = Position(offsetAsJson["file"].asText(), offsetAsJson["pos"].asLong())
            return retVal
        }

        override fun position(recordValue: DebeziumRecordValue): Position? {
            val file: String =
                recordValue.source["file"]?.takeIf { it.isTextual }?.asText() ?: return null
            val pos: Long =
                recordValue.source["pos"]?.takeIf { it.isIntegralNumber }?.asLong() ?: return null
            return Position(file, pos)
        }

        override fun position(sourceRecord: SourceRecord): Position? {
            val offset: Map<String, *> = sourceRecord.sourceOffset()
            val file: String = offset["file"]?.toString() ?: return null
            val pos: Long = offset["pos"] as? Long ?: return null
            return Position(file, pos)
        }

        override fun generateColdStartOffset(): DebeziumOffset {
            val position: Position = currentPosition()
            val timestamp: Instant = Instant.now()
            val key: ArrayNode =
                Jsons.arrayNode().apply {
                    add(container.databaseName)
                    add(Jsons.objectNode().apply { put("server", container.databaseName) })
                }
            val value: ObjectNode =
                Jsons.objectNode().apply {
                    put("ts_sec", timestamp.epochSecond)
                    put("file", position.file)
                    put("pos", position.pos)
                }
            return DebeziumOffset(mapOf(key to value))
        }

        override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
            DebeziumPropertiesBuilder()
                .with(generateWarmStartProperties(emptyList()))
                .with("snapshot.mode", "recovery")
                .withStreams(listOf())
                .buildMap()

        override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
            DebeziumPropertiesBuilder()
                .withDefault()
                .withConnector(MySqlConnector::class.java)
                .withDebeziumName(container.databaseName)
                .withHeartbeats(heartbeat)
                .with("include.schema.changes", "false")
                .with("connect.keep.alive.interval.ms", "1000")
                .withDatabase("hostname", container.host)
                .withDatabase("port", container.firstMappedPort.toString())
                .withDatabase("user", container.username)
                .withDatabase("password", container.password)
                .withDatabase("dbname", container.databaseName)
                .withDatabase("server.id", Random.Default.nextInt(5400..6400).toString())
                .withDatabase("include.list", container.databaseName)
                .withOffset()
                .withSchemaHistory()
                .with("snapshot.mode", "when_needed")
                .withStreams(streams)
                .buildMap()

        fun currentPosition(): Position =
            container.withStatement { statement: Statement ->
                statement.executeQuery("SHOW MASTER STATUS").use {
                    it.next()
                    Position(it.getString("File"), it.getLong("Position"))
                }
            }
    }
}
