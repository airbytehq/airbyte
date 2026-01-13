/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.operations.PostgresSourceStreamFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.Statement
import kotlin.use
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

class PostgresSourceCursorBasedIntegrationTest {
    @BeforeEach
    fun resetTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM public.$tableName")
            }
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO public.$tableName (k, v) VALUES (10, 'foo'), (20, 'bar')")
            }
        }
    }

    @Test
    fun testWithFullRefresh() {
        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()
        val recordMessageFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(2, recordMessageFromRun1.size)
        val lastStateMessageFromRun1 = run1.states().last()

        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog, listOf(lastStateMessageFromRun1))
                .run()
        val recordMessageFromRun2: List<AirbyteRecordMessage> = run2.records()
        assertEquals(0, recordMessageFromRun2.size)
    }

    companion object {
        val log = KotlinLogging.logger {}
        val dbContainer: PostgreSQLContainer<*> = PostgresContainerFactory.shared17()

        val config: PostgresSourceConfigurationSpecification =
            PostgresContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(PostgresSourceConfigurationFactory().make(config))
        }

        fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
            val desc = StreamDescriptor().withName(tableName).withNamespace("public")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns =
                        listOf(EmittedField("k", IntFieldType), EmittedField("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream =
                PostgresSourceStreamFactory(connectionFactory)
                    .create(PostgresSourceConfigurationFactory().make(config), discoveredStream)

            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .withCursorField(listOf("k"))
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            provisionTestContainer(connectionFactory)
        }

        lateinit var tableName: String

        fun provisionTestContainer(targetConnectionFactory: JdbcConnectionFactory) {
            tableName = (1..8).map { ('a'..'z').random() }.joinToString("")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute(
                        "CREATE TABLE public.$tableName(k bigint PRIMARY KEY, v VARCHAR(80))"
                    )
                }
            }
        }
    }
}
