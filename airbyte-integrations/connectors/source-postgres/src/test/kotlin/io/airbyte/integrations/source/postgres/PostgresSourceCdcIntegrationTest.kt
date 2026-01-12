/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.JdbcTestDbExecutor
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase.BaseImage
import io.airbyte.integrations.source.postgres.operations.PostgresSourceStreamFactory
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.Connection
import java.sql.Statement
import kotlin.use
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

class PostgresSourceCdcIntegrationTest {

    private val schema = TestAssetResourceNamer().getName()
    val configSpec = config(testdb.container, listOf(schema))
    val executor = JdbcTestDbExecutor(schema, jdbcConfig)
    private val jdbcConfig: JdbcSourceConfiguration
        get() = PostgresSourceConfigurationFactory().make(configSpec)

    companion object {
        fun config(
            postgresContainer: PostgreSQLContainer<*>,
            schemas: List<String> = listOf("public"),
        ): PostgresSourceConfigurationSpecification =
            PostgresSourceConfigurationSpecification().apply {
                host = postgresContainer.host
                port = postgresContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
                username = postgresContainer.username
                password = postgresContainer.password
                jdbcUrlParams = ""
                encryptionJson = EncryptionDisable
                database = "test"
                this.schemas = schemas
                checkpointTargetIntervalSeconds = 60
                max_db_connections = 1
                setIncrementalConfigurationSpecificationValue(
                    StandardReplicationMethodConfigurationSpecification
                )
            }

        private val testdb: PostgresTestDatabase = PostgresTestDatabase.`in`(this.serverImage)

        protected val serverImage: BaseImage
            get() = BaseImage.POSTGRES_17

        val config: PostgresSourceConfigurationSpecification = config(testdb.container)

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
