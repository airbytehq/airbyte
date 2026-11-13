/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.check.CloudHostCheck
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import java.net.ServerSocket
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * CHECK against a host that Airbyte Cloud can never reach. No database is involved: the port is one
 * nothing listens on, so without the host check every run would end in the network error.
 */
class MsSqlServerSourceCloudHostCheckTest {

    @Test
    fun testLocalhostWithoutTunnelOnCloudIsRejectedBeforeConnecting() {
        val output: BufferingOutputConsumer =
            CliRunner.source(
                    "check",
                    config("localhost"),
                    null,
                    null,
                    FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
                )
                .run()
        assertCheckFailedWith(output, CloudHostCheck.LOCAL_HOST_MESSAGE)
    }

    @Test
    fun testUrlShapedHostOnCloudIsRejectedBeforeConnecting() {
        val output: BufferingOutputConsumer =
            CliRunner.source(
                    "check",
                    config("sqlserver://user@host:1433/db"),
                    null,
                    null,
                    FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
                )
                .run()
        assertCheckFailedWith(output, CloudHostCheck.HOST_SYNTAX_MESSAGE)
    }

    @Test
    fun testLocalhostWithoutTunnelOutsideCloudGetsTheNetworkError() {
        val output: BufferingOutputConsumer = CliRunner.source("check", config("localhost")).run()
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertFalse(
            status.message.contains(CloudHostCheck.LOCAL_HOST_MESSAGE),
            status.message,
        )
        // The classifier rule from application.yml for a failed TCP/IP connection.
        Assertions.assertTrue(
            status.message.contains(
                "Airbyte could not reach SQL Server at the configured host and port",
            ),
            status.message,
        )
    }

    private fun assertCheckFailedWith(output: BufferingOutputConsumer, message: String) {
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertEquals(
            "Could not connect with provided configuration. Error: $message",
            status.message,
        )
        val error: AirbyteErrorTraceMessage =
            output.traces().single { it.type == AirbyteTraceMessage.Type.ERROR }.error
        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            error.failureType,
        )
        Assertions.assertEquals(message, error.message)
    }

    companion object {
        fun config(host: String): MsSqlServerSourceConfigurationSpecification =
            MsSqlServerSourceConfigurationSpecification().apply {
                this.host = host
                port = unusedPort()
                username = "sa"
                password = "Password123!"
                database = "master"
                jdbcUrlParams = ""
                // Passes the Cloud SSL requirement, so only the host can be at fault.
                setEncryptionValue(
                    MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification,
                )
                setIncrementalValue(UserDefinedCursor())
            }

        /** A port nothing listens on, so a connection attempt is refused immediately. */
        private fun unusedPort(): Int = ServerSocket(0).use { it.localPort }
    }
}
