/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.debezium.config.Configuration
import io.debezium.connector.postgresql.PostgresConnectorConfig
import io.debezium.connector.postgresql.PostgresValueConverter
import io.debezium.connector.postgresql.connection.PostgresConnection
import io.debezium.jdbc.JdbcConfiguration
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class PostgresSourceEmptyEnumCheckTest {

    @Test
    fun `finds empty enum types and validates after adding a label`() {
        connectionFactory.get().use { conn ->
            conn.createStatement().use { stmt ->
                stmt.execute("DROP TYPE IF EXISTS public.empty_enum;")
                stmt.execute("CREATE TYPE public.empty_enum AS ENUM ();")
            }

            try {
                assertEquals(
                    listOf("public.empty_enum"),
                    PostgresSourceMetadataQuerier.findEmptyEnumTypes(conn),
                )
                val exception =
                    assertThrows<ConfigErrorException> {
                        PostgresSourceMetadataQuerier.validateNoEmptyEnumTypes(conn)
                    }
                assertTrue(exception.message!!.contains("public.empty_enum"))

                conn.createStatement().use { stmt ->
                    stmt.execute("ALTER TYPE public.empty_enum ADD VALUE 'a';")
                }

                assertEquals(
                    emptyList<String>(),
                    PostgresSourceMetadataQuerier.findEmptyEnumTypes(conn),
                )
                assertDoesNotThrow { PostgresSourceMetadataQuerier.validateNoEmptyEnumTypes(conn) }
            } finally {
                conn.createStatement().use { stmt ->
                    stmt.execute("DROP TYPE IF EXISTS public.empty_enum;")
                }
            }
        }
    }

    @Test
    fun debeziumTypeRegistryFailsOnEmptyEnum() {
        connectionFactory.get().use { conn ->
            conn.createStatement().use { stmt ->
                stmt.execute("DROP TYPE IF EXISTS public.empty_enum;")
                stmt.execute("CREATE TYPE public.empty_enum AS ENUM ();")
            }

            try {
                val debeziumConfig = debeziumConfig()
                val exception =
                    assertThrows<Throwable> {
                        PostgresConnection(
                            JdbcConfiguration.adapt(debeziumConfig),
                            { registry ->
                                PostgresValueConverter.of(
                                    PostgresConnectorConfig(debeziumConfig),
                                    StandardCharsets.UTF_8,
                                    registry,
                                )
                            },
                            "empty-enum-test",
                        )
                    }
                val rootCause = generateSequence(exception) { it.cause }.last()
                assertTrue(rootCause is NullPointerException)
                assertTrue(rootCause.message?.contains("getArray") == true)

                conn.createStatement().use { stmt ->
                    stmt.execute("ALTER TYPE public.empty_enum ADD VALUE 'a';")
                }

                val postgresConnection =
                    PostgresConnection(
                        JdbcConfiguration.adapt(debeziumConfig),
                        { registry ->
                            PostgresValueConverter.of(
                                PostgresConnectorConfig(debeziumConfig),
                                StandardCharsets.UTF_8,
                                registry,
                            )
                        },
                        "empty-enum-test",
                    )
                postgresConnection.close()
            } finally {
                conn.createStatement().use { stmt ->
                    stmt.execute("DROP TYPE IF EXISTS public.empty_enum;")
                }
            }
        }
    }

    companion object {
        private lateinit var connectionFactory: JdbcConnectionFactory
        private lateinit var testdb: PostgresTestDatabase

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startTestContainer() {
            testdb = PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17)
            val configSpec = PostgresSourceCdcIntegrationTest.config(testdb.container)
            connectionFactory =
                JdbcConnectionFactory(PostgresSourceConfigurationFactory().make(configSpec))
        }

        private fun debeziumConfig(): Configuration =
            Configuration.create()
                .with("database.hostname", testdb.container.host)
                .with("database.port", testdb.container.getMappedPort(5432))
                .with("database.user", testdb.container.username)
                .with("database.password", testdb.container.password)
                .with("database.dbname", testdb.container.databaseName)
                .with("topic.prefix", "empty-enum-test")
                .build()
    }
}
