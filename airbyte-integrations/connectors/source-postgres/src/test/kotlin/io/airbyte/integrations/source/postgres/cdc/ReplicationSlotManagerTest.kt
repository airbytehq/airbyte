/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.DefaultExceptionClassifier
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.connection.Lsn
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class ReplicationSlotManagerTest {

    @Test
    fun `validate reports a config error when the replication slot is missing`() {
        val manager = managerForReplicationSlotQuery(resultSet = resultSetWithRows(rowCount = 0))

        val thrown =
            assertThrows(RuntimeException::class.java) {
                manager.validate(Lsn.valueOf("0/16B6C50"))
            }

        assertReplicationSlotConfigError(
            thrown,
            displayMessage = "Postgres CDC replication slot is missing.",
            internalMessage =
                "No pgoutput replication slot matched configured replication slot 'configured_slot' in database 'postgres'."
        )
    }

    @Test
    fun `validate reports a config error when multiple replication slots match`() {
        val manager = managerForReplicationSlotQuery(resultSet = resultSetWithRows(rowCount = 2))

        val thrown =
            assertThrows(RuntimeException::class.java) {
                manager.validate(Lsn.valueOf("0/16B6C50"))
            }

        assertReplicationSlotConfigError(
            thrown,
            displayMessage = "Postgres CDC replication slot is not unique.",
            internalMessage =
                "Multiple pgoutput replication slots matched configured replication slot 'configured_slot' in database 'postgres'."
        )
    }

    private fun assertReplicationSlotConfigError(
        thrown: RuntimeException,
        displayMessage: String,
        internalMessage: String,
    ) {
        assertEquals(internalMessage, thrown.message)
        val configError = assertInstanceOf(ConfigErrorException::class.java, thrown.cause)
        assertEquals(displayMessage, configError.message)
        assertEquals(
            ConfigError(displayMessage),
            DefaultExceptionClassifier(orderValue = 1).classify(thrown)
        )
    }

    private fun managerForReplicationSlotQuery(resultSet: ResultSet): ReplicationSlotManager {
        val config = postgresConfig()
        val connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>()
        val connection = mockk<Connection>()
        val statement = mockk<PreparedStatement>()

        every { connectionFactory.get() } returns connection
        every { connection.prepareStatement(any()) } returns statement
        every { statement.setString(any(), any()) } just runs
        every { statement.executeQuery() } returns resultSet
        every { resultSet.close() } just runs
        every { statement.close() } just runs
        every { connection.close() } just runs

        return ReplicationSlotManager(config = config, connectionFactory = connectionFactory)
    }

    private fun resultSetWithRows(rowCount: Int): ResultSet {
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns (rowCount > 0)
        if (rowCount > 0) {
            every { resultSet.isLast } returns (rowCount == 1)
        }
        return resultSet
    }

    private fun postgresConfig(): PostgresSourceConfiguration {
        val cdcConfig =
            CdcIncrementalConfiguration(
                initialLoadTimeout = Duration.ofHours(8),
                invalidCdcCursorPositionBehavior = InvalidCdcCursorPositionBehavior.FAIL_SYNC,
                shutdownTimeout = Duration.ofSeconds(60),
                replicationSlot = "configured_slot",
                publication = "configured_publication",
                debeziumCommitsLsn = false,
                heartbeatActionQuery = null,
                airbyteHeartbeatTimeout = Duration.ofMinutes(20),
            )

        return PostgresSourceConfiguration(
            realHost = "localhost",
            realPort = 5432,
            sshTunnel = null,
            sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
            jdbcUrlFmt = "jdbc:postgresql://%s:%d/postgres",
            jdbcProperties = mapOf("user" to "airbyte", "password" to "password"),
            database = "postgres",
            namespaces = setOf("public"),
            incrementalConfiguration = cdcConfig,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.ofSeconds(60),
            checkPrivileges = true,
        )
    }
}
