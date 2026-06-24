/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException
import org.postgresql.util.PSQLState

class PostgresSourceJdbcConnectionFactoryTest {

    private fun buildFactory(): PostgresSourceJdbcConnectionFactory {
        val config =
            mockk<PostgresSourceConfiguration> {
                every { jdbcProperties } returns
                    mapOf("user" to "testuser", "password" to "testpass")
                every { jdbcUrlFmt } returns "jdbc:postgresql://%s:%d/testdb"
                every { realHost } returns "localhost"
                every { realPort } returns 5432
            }
        return PostgresSourceJdbcConnectionFactory(config)
    }

    private fun invokeValidateReplicationConnection(
        factory: PostgresSourceJdbcConnectionFactory,
        connection: Connection,
    ) {
        val method =
            PostgresSourceJdbcConnectionFactory::class
                .java
                .getDeclaredMethod("validateReplicationConnection", Connection::class.java)
        method.isAccessible = true
        try {
            method.invoke(factory, connection)
        } catch (e: java.lang.reflect.InvocationTargetException) {
            throw e.targetException
        }
    }

    @Test
    fun `validateReplicationConnection succeeds when IDENTIFY_SYSTEM returns a row`() {
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { close() } returns Unit
            }
        val statement =
            mockk<Statement> {
                every { executeQuery("IDENTIFY_SYSTEM") } returns resultSet
                every { close() } returns Unit
            }
        val connection = mockk<Connection> { every { createStatement() } returns statement }

        val factory = buildFactory()
        invokeValidateReplicationConnection(factory, connection)
    }

    @Test
    fun `validateReplicationConnection throws ConfigErrorException when IDENTIFY_SYSTEM returns empty result`() {
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns false
                every { close() } returns Unit
            }
        val statement =
            mockk<Statement> {
                every { executeQuery("IDENTIFY_SYSTEM") } returns resultSet
                every { close() } returns Unit
            }
        val connection = mockk<Connection> { every { createStatement() } returns statement }

        val factory = buildFactory()
        val ex =
            assertThrows(ConfigErrorException::class.java) {
                invokeValidateReplicationConnection(factory, connection)
            }
        assertEquals("The DB connection is not a valid replication connection", ex.message)
    }

    @Test
    fun `validateReplicationConnection throws ConfigErrorException on PSQLException from IDENTIFY_SYSTEM`() {
        val psqlException =
            PSQLException("syntax error at or near \"IDENTIFY_SYSTEM\"", PSQLState.SYNTAX_ERROR)
        val statement =
            mockk<Statement> {
                every { executeQuery("IDENTIFY_SYSTEM") } throws psqlException
                every { close() } returns Unit
            }
        val connection = mockk<Connection> { every { createStatement() } returns statement }

        val factory = buildFactory()
        val ex =
            assertThrows(ConfigErrorException::class.java) {
                invokeValidateReplicationConnection(factory, connection)
            }
        assertTrue(
            ex.message!!.contains("does not support the replication protocol"),
            "Expected message about replication protocol, got: ${ex.message}",
        )
        assertEquals(psqlException, ex.cause)
    }
}
