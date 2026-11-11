/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.check.CloudHostCheck
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.net.ServerSocket
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * The stepped setup form without a database: the layout the spec declares, the partial
 * configurations the form sends to a section-aware CHECK and the field each section insists on.
 * What happens on the server is covered by [PostgresSourceCheckSectionIntegrationTest].
 */
class PostgresSourceCheckSectionTest {

    @Test
    fun testSpecSections() {
        val spec: JsonNode = spec()
        // The sections in form order with the groups each one shows; every section is checkable.
        Assertions.assertEquals(
            listOf(
                "connection" to listOf("network", "connection_advanced"),
                "credentials" to listOf("db", "auth"),
                "sync_method" to listOf("sync"),
                "review" to listOf("advanced"),
            ),
            spec["sections"].map { it["id"].asText() to it["groups"].map(JsonNode::asText) },
        )
        Assertions.assertEquals(
            listOf(0, 1, 2, 3),
            spec["sections"].map { it["order"].asInt() },
        )
        Assertions.assertTrue(
            spec["sections"].all { it["check"].isBoolean && it["check"].asBoolean() },
        )
        // Every group belongs to exactly one section, and the groups are declared in form order.
        Assertions.assertEquals(
            spec["sections"].flatMap { it["groups"].map(JsonNode::asText) },
            spec["groups"].map { it["id"].asText() },
        )
    }

    @Test
    fun testSpecFieldsOfEachGroup() {
        // Every property names a group; within a group the form follows `order`.
        val fieldsByGroup: Map<String, List<String>> =
            spec()["properties"]
                .properties()
                .sortedBy { it.value["order"].asInt() }
                .groupBy({ it.value["group"].asText() }, { it.key })
        Assertions.assertEquals(
            mapOf(
                "network" to listOf("tunnel_method", "host", "port"),
                "connection_advanced" to listOf("ssl_mode", "jdbc_url_params"),
                "db" to listOf("database", "schemas"),
                "auth" to
                    listOf(
                        "username",
                        "password",
                        "entra_service_principal_auth",
                        "entra_tenant_id",
                        "entra_client_id",
                    ),
                "sync" to listOf("replication_method"),
                "advanced" to
                    listOf(
                        "check_privileges",
                        "checkpoint_target_interval_seconds",
                        "max_db_connections",
                    ),
            ),
            fieldsByGroup,
        )
    }

    @Test
    fun testSpecConnectionMethod() {
        val spec: JsonNode = spec()
        val method: JsonNode = spec["properties"]["tunnel_method"]
        Assertions.assertEquals("Connection method", method["title"].asText())
        Assertions.assertEquals("radio", method["display_type"].asText())
        // The tiles carry the wording of the form; the JSON under them is the CDK's, unchanged.
        Assertions.assertEquals(
            listOf(
                "Direct connection" to "NO_TUNNEL",
                "SSH tunnel with key authentication" to "SSH_KEY_AUTH",
                "SSH tunnel with password authentication" to "SSH_PASSWORD_AUTH",
            ),
            method["oneOf"].map {
                it["title"].asText() to it["properties"]["tunnel_method"]["enum"].single().asText()
            },
        )
        Assertions.assertEquals(
            listOf(
                listOf("tunnel_method"),
                listOf("tunnel_method", "tunnel_host", "tunnel_port", "tunnel_user", "ssh_key"),
                listOf(
                    "tunnel_method",
                    "tunnel_host",
                    "tunnel_port",
                    "tunnel_user",
                    "tunnel_user_password",
                ),
            ),
            method["oneOf"].map { it["required"].map(JsonNode::asText) },
        )
        // The database host and port are fields of the section, next to the tiles and not inside
        // one: an SSH tunnel needs them as much as a direct connection does.
        val required: List<String> = spec["required"].map(JsonNode::asText)
        Assertions.assertTrue(required.containsAll(listOf("tunnel_method", "host", "port")))
        Assertions.assertTrue(
            method["oneOf"].none { it["properties"].has("host") || it["properties"].has("port") },
        )
    }

    @Test
    fun testConnectionSectionThroughAnSshTunnelRequiresTheDatabaseHost() {
        assertFailedWith(
            check(
                """{"check-section":"connection","port":5432,
                   "tunnel_method":{"tunnel_method":"SSH_PASSWORD_AUTH",
                     "tunnel_host":"jump.example.com","tunnel_port":22,
                     "tunnel_user":"sshuser","tunnel_user_password":"secret"}}""",
            ),
            "The 'connection' section check requires the 'host' field.",
        )
    }

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

    private fun spec(): JsonNode =
        CliRunner.source("spec").run().specs().single().connectionSpecification

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
