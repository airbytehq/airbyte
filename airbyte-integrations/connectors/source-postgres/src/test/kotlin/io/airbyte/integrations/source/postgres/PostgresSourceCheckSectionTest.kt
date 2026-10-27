/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.check.CloudHostCheck
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.net.ServerSocket
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * Section-aware CHECK without a database: the partial configurations the stepped setup form sends
 * and the field each section insists on. What happens on the server is covered by
 * [PostgresSourceCheckSectionIntegrationTest].
 */
class PostgresSourceCheckSectionTest {

    @Test
    fun testConnectionSectionRequiresTheHost() {
        assertFailedWith(
            check("""{"check-section":"connection","port":5432}"""),
            "The 'connection' section check requires the 'host' field.",
        )
    }

    @Test
    fun testConnectionSectionProbesTheServerWithoutCredentials() {
        // No database, username or password, and the probe still reaches the (closed) port.
        val output: BufferingOutputConsumer =
            check(
                """{"check-section":"connection","host":"localhost","port":${unusedPort()},
                   "ssl_mode":{"mode":"disable"}}""",
            )
        assertFailedContaining(
            output,
            "Airbyte could not reach the database at the configured host and port",
        )
    }

    @Test
    fun testConnectionSectionAppliesTheCloudHostRule() {
        val output: BufferingOutputConsumer =
            check(
                """{"check-section":"connection","host":"localhost","port":${unusedPort()},
                   "ssl_mode":{"mode":"require"}}""",
                FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
            )
        assertFailedWith(output, CloudHostCheck.LOCAL_HOST_MESSAGE)
    }

    @Test
    fun testConnectionSectionAppliesTheCloudSslRule() {
        // Rejected before any connection attempt, so the host never resolves.
        val output: BufferingOutputConsumer =
            check(
                """{"check-section":"connection","host":"db.example.com","port":5432,
                   "ssl_mode":{"mode":"disable"}}""",
                FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT,
            )
        assertFailedContaining(
            output,
            "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel",
        )
    }

    @Test
    fun testCredentialsSectionRequiresTheDatabase() {
        assertFailedWith(
            check(
                """{"check-section":"credentials","host":"localhost","port":5432,
                   "username":"airbyte","password":"secret"}""",
            ),
            "The 'credentials' section check requires the 'database' field.",
        )
    }

    @Test
    fun testCredentialsSectionRequiresTheUsername() {
        assertFailedWith(
            check(
                """{"check-section":"credentials","host":"localhost","port":5432,
                   "database":"test","password":"secret"}""",
            ),
            "The 'credentials' section check requires the 'username' field.",
        )
    }

    @Test
    fun testCredentialsSectionRequiresTheEntraIdsForAServicePrincipal() {
        assertFailedWith(
            check(
                """{"check-section":"credentials","host":"localhost","port":5432,
                   "database":"test","username":"airbyte","password":"secret",
                   "entra_service_principal_auth":true}""",
            ),
            "The 'credentials' section check requires the 'entra_tenant_id' field.",
        )
    }

    @Test
    fun testSyncMethodSectionRequiresTheSlotForCdc() {
        assertFailedWith(
            check(
                """{"check-section":"sync_method","host":"localhost","port":5432,
                   "database":"test","username":"airbyte",
                   "replication_method":{"method":"CDC","publication":"pub"}}""",
            ),
            "The 'sync_method' section check requires the 'replication_slot' field.",
        )
    }

    @Test
    fun testUnknownSection() {
        assertFailedWith(
            check("""{"check-section":"nope","host":"localhost"}"""),
            "Unknown check-section 'nope'; the connector specification declares: " +
                "connection, credentials, sync_method, review.",
        )
    }

    private fun check(
        configJson: String,
        vararg featureFlags: FeatureFlag,
    ): BufferingOutputConsumer =
        CliRunner.source("check", configJson, null, null, *featureFlags).run()

    private fun assertFailedWith(output: BufferingOutputConsumer, message: String) {
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertEquals(
            "Could not connect with provided configuration. Error: $message",
            status.message,
        )
    }

    private fun assertFailedContaining(output: BufferingOutputConsumer, fragment: String) {
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.status)
        Assertions.assertTrue(status.message.contains(fragment), status.message)
    }

    /** A port nothing listens on, so a connection attempt is refused immediately. */
    private fun unusedPort(): Int = ServerSocket(0).use { it.localPort }
}
