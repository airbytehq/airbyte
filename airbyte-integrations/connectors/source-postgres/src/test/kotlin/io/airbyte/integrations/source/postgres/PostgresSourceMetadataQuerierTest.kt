/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.mockk.every
import io.mockk.mockk
import java.time.Duration
import kotlin.time.Duration.Companion.ZERO
import kotlin.time.Duration.Companion.milliseconds
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class PostgresSourceMetadataQuerierTest {

    @Test
    fun `extraChecks rejects insufficient SSL mode without SSH tunnel on Cloud`() {
        val querier = cloudQuerier(sslMode = "allow")

        val exception = assertThrows<ConfigErrorException> { querier.extraChecks() }

        assertEquals(CLOUD_SSL_ERROR_MESSAGE, exception.message)
    }

    @Test
    fun `extraChecks allows required SSL mode without SSH tunnel on Cloud`() {
        val querier = cloudQuerier(sslMode = "require")

        assertDoesNotThrow { querier.extraChecks() }
    }

    @Test
    fun `extraChecks allows insufficient SSL mode with SSH tunnel on Cloud`() {
        val querier =
            cloudQuerier(
                sslMode = "allow",
                sshTunnel = SshPasswordAuthTunnelMethod("localhost", 22, "sshuser", "secret")
            )

        assertDoesNotThrow { querier.extraChecks() }
    }

    @Test
    fun `extraChecks allows insufficient SSL mode without SSH tunnel outside Cloud`() {
        val querier =
            PostgresSourceMetadataQuerier(
                base = noopMetadataQuerier(),
                postgresSourceConfig = config(sslMode = "allow"),
                featureFlags = emptySet()
            )

        assertDoesNotThrow { querier.extraChecks() }
    }

    private fun cloudQuerier(
        sslMode: String,
        sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    ): PostgresSourceMetadataQuerier =
        PostgresSourceMetadataQuerier(
            base = noopMetadataQuerier(),
            postgresSourceConfig = config(sslMode = sslMode, sshTunnel = sshTunnel),
            featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        )

    private fun config(
        sslMode: String,
        sshTunnel: SshTunnelMethodConfiguration = SshNoTunnelMethod,
    ): PostgresSourceConfiguration =
        PostgresSourceConfiguration(
            realHost = "localhost",
            realPort = 5432,
            sshTunnel = sshTunnel,
            sshConnectionOptions =
                SshConnectionOptions(1_000.milliseconds, 2_000.milliseconds, ZERO),
            jdbcUrlFmt = "jdbc:postgresql://%s:%d/postgres",
            jdbcProperties = mapOf("sslmode" to sslMode),
            database = "postgres",
            namespaces = emptySet(),
            incrementalConfiguration = UserDefinedCursorIncrementalConfiguration,
            maxConcurrency = 1,
            resourceAcquisitionHeartbeat = Duration.ofMillis(100),
            checkpointTargetInterval = Duration.ofSeconds(300),
            checkPrivileges = true,
        )

    private fun noopMetadataQuerier(): JdbcMetadataQuerier =
        mockk<JdbcMetadataQuerier>(relaxed = true) { every { extraChecks() } returns Unit }

    private companion object {
        const val CLOUD_SSL_ERROR_MESSAGE =
            "Airbyte Cloud Postgres sources require SSL mode require, verify-ca, verify-full, or an SSH tunnel."
    }
}
