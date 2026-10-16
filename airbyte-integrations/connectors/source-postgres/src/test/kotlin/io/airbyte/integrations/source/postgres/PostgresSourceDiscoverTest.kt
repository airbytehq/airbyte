/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.integrations.source.postgres.config.CdcReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.IncrementalConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.XminReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Discovery of the three stream shapes that decide sync modes, cursor and resumability: a table
 * with a primary key, a table without one, and a view.
 *
 * The expected values are what `airbyte/source-postgres:3.7.2 discover` emits for the same DDL. The
 * Bulk CDK rewrite gated the xmin cursor and `is_resumable` on the primary key, which left PK-less
 * tables advertising INCREMENTAL without a cursor
 * (https://github.com/airbytehq/airbyte/issues/81431).
 */
class PostgresSourceDiscoverTest {

    @Test
    fun xmin() {
        val streams = discover(XminReplicationMethodConfigurationSpecification)
        assertStream(
            streams.getValue(WITH_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = true,
            primaryKey = listOf(listOf("id")),
            isResumable = true,
        )
        assertStream(
            streams.getValue(WITHOUT_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = true,
            primaryKey = listOf(),
            isResumable = true,
        )
        assertStream(
            streams.getValue(VIEW),
            syncModes = listOf(SyncMode.FULL_REFRESH),
            sourceDefinedCursor = false,
            primaryKey = listOf(),
            isResumable = false,
        )
    }

    @Test
    fun standard() {
        val streams = discover(StandardReplicationMethodConfigurationSpecification)
        assertStream(
            streams.getValue(WITH_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = false,
            primaryKey = listOf(listOf("id")),
            isResumable = true,
        )
        assertStream(
            streams.getValue(WITHOUT_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = false,
            primaryKey = listOf(),
            isResumable = true,
        )
        assertStream(
            streams.getValue(VIEW),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = false,
            primaryKey = listOf(),
            isResumable = false,
        )
    }

    @Test
    fun cdc() {
        val streams =
            discover(
                CdcReplicationMethodConfigurationSpecification().apply {
                    replicationSlot = "airbyte_slot"
                    publication = "airbyte_publication"
                }
            )
        assertStream(
            streams.getValue(WITH_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            sourceDefinedCursor = true,
            primaryKey = listOf(listOf("id")),
            isResumable = true,
        )
        assertStream(
            streams.getValue(WITHOUT_PK),
            syncModes = listOf(SyncMode.FULL_REFRESH),
            sourceDefinedCursor = false,
            primaryKey = listOf(),
            isResumable = true,
        )
        assertStream(
            streams.getValue(VIEW),
            syncModes = listOf(SyncMode.FULL_REFRESH),
            sourceDefinedCursor = false,
            primaryKey = listOf(),
            isResumable = false,
        )
    }

    private fun discover(
        method: IncrementalConfigurationSpecification,
    ): Map<String, AirbyteStream> {
        val configSpec: PostgresSourceConfigurationSpecification =
            config(testdb, listOf(schema)).apply {
                setIncrementalConfigurationSpecificationValue(method)
            }
        val catalog = CliRunner.source("discover", configSpec).run().catalogs().single()
        val streams: Map<String, AirbyteStream> = catalog.streams.associateBy { it.name }
        Assertions.assertEquals(setOf(WITH_PK, WITHOUT_PK, VIEW), streams.keys)
        return streams
    }

    private fun assertStream(
        stream: AirbyteStream,
        syncModes: List<SyncMode>,
        sourceDefinedCursor: Boolean,
        primaryKey: List<List<String>>,
        isResumable: Boolean,
    ) {
        Assertions.assertAll(
            stream.name,
            {
                Assertions.assertEquals(
                    syncModes,
                    stream.supportedSyncModes,
                    "supported_sync_modes"
                )
            },
            {
                Assertions.assertEquals(
                    sourceDefinedCursor,
                    stream.sourceDefinedCursor == true,
                    "source_defined_cursor",
                )
            },
            {
                Assertions.assertEquals(
                    primaryKey,
                    stream.sourceDefinedPrimaryKey,
                    "source_defined_primary_key",
                )
            },
            { Assertions.assertEquals(isResumable, stream.isResumable == true, "is_resumable") },
        )
    }

    companion object {
        private const val WITH_PK = "with_pk"
        private const val WITHOUT_PK = "without_pk"
        private const val VIEW = "v_with_pk"

        private val schema: String = TestAssetResourceNamer().getName()
        private lateinit var testdb: PostgresTestDatabase

        fun config(
            testdb: PostgresTestDatabase,
            schemas: List<String>
        ): PostgresSourceConfigurationSpecification =
            PostgresSourceConfigurationSpecification().apply {
                host = testdb.container.host
                port = testdb.container.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
                username = testdb.userName
                password = testdb.password
                jdbcUrlParams = ""
                encryptionJson = EncryptionDisable
                database = testdb.databaseName
                this.schemas = schemas
                checkpointTargetIntervalSeconds = 60
                maxDbConnections = 1
            }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            // Same shape as the audit tables in airbytehq/airbyte#81431: a uuid key, a column
            // named after a reserved word and a jsonb payload.
            testdb =
                PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17)
                    .with("CREATE SCHEMA \"$schema\"")
                    .with(
                        "CREATE TABLE \"$schema\".$WITH_PK(id uuid PRIMARY KEY, " +
                            "\"timestamp\" timestamptz NOT NULL, payload jsonb)"
                    )
                    .with(
                        "CREATE TABLE \"$schema\".$WITHOUT_PK(id uuid NOT NULL, " +
                            "\"timestamp\" timestamptz NOT NULL, payload jsonb)"
                    )
                    .with("CREATE VIEW \"$schema\".$VIEW AS SELECT * FROM \"$schema\".$WITH_PK")
        }
    }
}
