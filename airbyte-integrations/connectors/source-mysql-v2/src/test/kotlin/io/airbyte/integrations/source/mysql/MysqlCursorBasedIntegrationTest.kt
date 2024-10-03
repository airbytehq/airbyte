/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mysql.MysqlContainerFactory.execAsRoot
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

class MysqlCursorBasedIntegrationTest {

    @Test
    fun testCursorBasedRead() {
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config(), configuredCatalog).run()
        println("Run1:" + run1.messages())


        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO test.tbl (k, v) VALUES ('3', 'baz')")
            }
        }

        val run2InputState: List<AirbyteStateMessage> = listOf(run1.states().last())
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config(), configuredCatalog, run2InputState).run()
        println(run2.messages())

    }

    companion object {
        val log = KotlinLogging.logger {}
        lateinit var dbContainer: MySQLContainer<*>

        fun config(): MysqlSourceConfigurationJsonObject =
            MysqlContainerFactory.config(dbContainer).apply { setCursorMethodValue(UserDefinedCursor) }

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MysqlSourceConfigurationFactory().make(config()))
        }

        val configuredCatalog: ConfiguredAirbyteCatalog = run {
            val desc = StreamDescriptor().withName("tbl").withNamespace("test")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns = listOf(Field("k", StringFieldType), Field("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream = JdbcAirbyteStreamFactory().createGlobal(discoveredStream)
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .withCursorField(listOf("k"))
            ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MysqlContainerFactory.exclusive(
                    imageName = "mysql:8.0",
                    MysqlContainerFactory.WithNetwork,
                )
            provisionTestContainer(dbContainer, connectionFactory)
        }

        fun provisionTestContainer(
            targetContainer: MySQLContainer<*>,
            targetConnectionFactory: JdbcConnectionFactory
        ) {
            val grant =
                "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT " +
                    "ON *.* TO '${targetContainer.username}'@'%';"
            targetContainer.execAsRoot(grant)
            targetContainer.execAsRoot("FLUSH PRIVILEGES;")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE test.tbl(k VARCHAR(20) PRIMARY KEY, v VARCHAR(80))")
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("INSERT INTO test.tbl (k, v) VALUES ('1', 'foo'), ('2', 'bar')")
                }
            }
        }
    }
}
