/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.SECTION_CONNECTION
import io.airbyte.integrations.source.postgres.config.SECTION_CREDENTIALS
import io.airbyte.integrations.source.postgres.config.SECTION_REVIEW
import io.airbyte.integrations.source.postgres.config.SECTION_SYNC_METHOD
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase.BaseImage
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase.ContainerModifier
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import java.net.ServerSocket
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Section-aware CHECK against a live Postgres: every section's probe, with the configuration
 * narrowed to what the stepped setup form has collected by then.
 */
class PostgresSourceCheckSectionIntegrationTest {

    @Test
    fun testConnectionSectionWithoutCredentials() {
        assertSucceeded(check(connection()))
    }

    @Test
    fun testConnectionSectionWithAClosedPort() {
        assertFailedContaining(
            check(connection().put("port", unusedPort())),
            "Airbyte could not reach the database at the configured host and port",
        )
    }

    @Test
    fun testCredentialsSection() {
        assertSucceeded(check(credentials()))
    }

    @Test
    fun testCredentialsSectionWithAWrongPassword() {
        assertFailedContaining(
            check(credentials().put("password", "wrong")),
            "password authentication failed",
        )
    }

    @Test
    fun testCredentialsSectionWithAMissingDatabase() {
        assertFailedContaining(
            check(credentials().put("database", "no_such_db")),
            "database \"no_such_db\" does not exist",
        )
    }

    @Test
    fun testSyncMethodSectionStandard() {
        assertSucceeded(check(syncMethod(replicationMethod("Standard"))))
    }

    @Test
    fun testSyncMethodSectionXmin() {
        assertSucceeded(check(syncMethod(replicationMethod("Xmin"))))
    }

    @Test
    fun testSyncMethodSectionCdc() {
        assertSucceeded(check(syncMethod(cdc(testdb.replicationSlotName, testdb.publicationName))))
    }

    @Test
    fun testSyncMethodSectionCdcWithAMissingSlot() {
        assertFailedWith(
            check(syncMethod(cdc("no_such_slot", testdb.publicationName))),
            "Replication slot 'no_such_slot' does not exist in database '${testdb.databaseName}'.",
        )
    }

    @Test
    fun testSyncMethodSectionCdcWithAMissingPublication() {
        assertFailedWith(
            check(syncMethod(cdc(testdb.replicationSlotName, "no_such_publication"))),
            "Publication 'no_such_publication' does not exist " +
                "in database '${testdb.databaseName}'.",
        )
    }

    @Test
    fun testSyncMethodSectionCdcWithoutLogicalWalLevel() {
        val plainDb: PostgresTestDatabase = PostgresTestDatabase.`in`(BaseImage.POSTGRES_17)
        try {
            assertFailedWith(
                check(syncMethod(cdc("any_slot", "any_publication"), plainDb)),
                "CDC requires the server setting wal_level = logical; it is 'replica'.",
            )
        } finally {
            plainDb.close()
        }
    }

    @Test
    fun testReviewSectionIsTheFullCheck() {
        assertSucceeded(check(complete().put("check-section", SECTION_REVIEW)))
        // Only the full check discovers tables.
        val noTables: ObjectNode = complete().put("check-section", SECTION_REVIEW)
        noTables.putArray("schemas").add("no_such_schema")
        assertFailedContaining(check(noTables), "No tables are visible to the configured user")
    }

    @Test
    fun testFullCheckWithoutASection() {
        assertSucceeded(check(complete()))
    }

    /** The connection section: host, port and SSL mode; no database, user or password. */
    private fun connection(db: PostgresTestDatabase = testdb): ObjectNode =
        Jsons.createObjectNode().apply {
            put("check-section", SECTION_CONNECTION)
            put("host", db.container.host)
            put("port", db.container.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT))
            putObject("ssl_mode").put("mode", "disable")
        }

    private fun credentials(db: PostgresTestDatabase = testdb): ObjectNode =
        connection(db).apply {
            put("check-section", SECTION_CREDENTIALS)
            put("database", db.databaseName)
            put("username", db.userName)
            put("password", db.password)
        }

    private fun syncMethod(
        replicationMethod: ObjectNode,
        db: PostgresTestDatabase = testdb,
    ): ObjectNode =
        credentials(db).apply {
            put("check-section", SECTION_SYNC_METHOD)
            set<ObjectNode>("replication_method", replicationMethod)
        }

    /** The complete configuration, as the review section or a plain CHECK sends it. */
    private fun complete(): ObjectNode =
        syncMethod(replicationMethod("Standard")).apply {
            remove("check-section")
            putArray("schemas").add("public")
        }

    private fun replicationMethod(method: String): ObjectNode =
        Jsons.createObjectNode().put("method", method)

    private fun cdc(slot: String?, publication: String?): ObjectNode =
        replicationMethod("CDC").put("replication_slot", slot).put("publication", publication)

    private fun check(config: ObjectNode): BufferingOutputConsumer =
        CliRunner.source("check", Jsons.writeValueAsString(config)).run()

    private fun assertSucceeded(output: BufferingOutputConsumer) {
        val status: AirbyteConnectionStatus = output.statuses().single()
        Assertions.assertEquals(
            AirbyteConnectionStatus.Status.SUCCEEDED,
            status.status,
            status.message,
        )
    }

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

    private fun unusedPort(): Int = ServerSocket(0).use { it.localPort }

    companion object {
        private lateinit var testdb: PostgresTestDatabase

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startDatabase() {
            testdb =
                PostgresTestDatabase.`in`(
                        BaseImage.POSTGRES_17,
                        ContainerModifier.WAL_LEVEL_LOGICAL,
                    )
                    // The full check needs at least one table to query.
                    .with("CREATE TABLE public.section_check(id INT PRIMARY KEY)")
                    .withReplicationSlot()
                    .withPublicationForAllTables()
        }

        @JvmStatic
        @AfterAll
        fun stopDatabase() {
            testdb.close()
        }
    }
}
