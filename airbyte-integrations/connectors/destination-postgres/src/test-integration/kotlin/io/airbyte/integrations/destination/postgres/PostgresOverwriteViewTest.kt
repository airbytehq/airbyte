/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.schema.PostgresColumnManager
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.mockk.every
import io.mockk.mockk
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource
import org.postgresql.util.PSQLException

class PostgresOverwriteViewTest {
    private lateinit var dataSource: HikariDataSource
    private lateinit var namespace: String

    @BeforeEach
    fun setup() {
        PostgresContainerHelper.start()
        dataSource =
            HikariDataSource(
                HikariConfig().apply {
                    jdbcUrl =
                        "jdbc:postgresql://${PostgresContainerHelper.getHost()}:${PostgresContainerHelper.getPort()}/${PostgresContainerHelper.getDatabaseName()}"
                    username = PostgresContainerHelper.getUsername()
                    password = PostgresContainerHelper.getPassword()
                    maximumPoolSize = 1
                },
            )
        namespace = "overwrite_${UUID.randomUUID().toString().replace("-", "") }"
        execute("CREATE SCHEMA \"$namespace\"")
        execute("CREATE VIEW \"$namespace\".target AS SELECT 1 AS value")
        execute("CREATE VIEW \"$namespace\".dependent AS SELECT * FROM \"$namespace\".target")
    }

    @AfterEach
    fun cleanup() {
        dataSource.use { execute("DROP SCHEMA \"$namespace\" CASCADE") }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun overwriteViewWithDependentView(dropCascade: Boolean) = runBlocking {
        execute("CREATE TABLE \"$namespace\".source AS SELECT 42 AS value")

        client(dropCascade)
            .overwriteTable(
                TableName(namespace, "source"),
                TableName(namespace, "target"),
            )

        assertEquals(42, query("SELECT value FROM \"$namespace\".target"))
        assertNull(query("SELECT to_regclass('$namespace.source')"))
        assertNull(query("SELECT to_regclass('$namespace.dependent')"))
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun failedReplacementPreservesViewAndDependents(dropCascade: Boolean) {
        val error =
            assertThrows<PSQLException> {
                runBlocking {
                    client(dropCascade)
                        .overwriteTable(
                            TableName(namespace, "missing_source"),
                            TableName(namespace, "target"),
                        )
                }
            }

        assertEquals("42P01", error.sqlState)
        assertEquals(1, query("SELECT value FROM \"$namespace\".target"))
        assertEquals(1, query("SELECT value FROM \"$namespace\".dependent"))
    }

    private fun client(dropCascade: Boolean): PostgresAirbyteClient {
        val configuration =
            mockk<PostgresConfiguration> {
                every { this@mockk.dropCascade } returns dropCascade
                every { legacyRawTablesOnly } returns false
            }
        val columnManager = PostgresColumnManager(configuration)
        return PostgresAirbyteClient(
            dataSource,
            PostgresDirectLoadSqlGenerator(columnManager, configuration),
            columnManager,
            configuration,
            metaColumnRepairEnabled = false,
        )
    }

    private fun execute(sql: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { it.execute(sql) }
        }
    }

    private fun query(sql: String): Any? =
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery(sql).use {
                    it.next()
                    it.getObject(1)
                }
            }
        }
}
