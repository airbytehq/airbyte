/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.integrations.source.postgres.config.CdcReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.protocol.models.v0.SyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

/** CDC discover: only tables in the publication can be read incrementally. */
class PostgresSourceCdcPublicationSyncModesTest {

    @Test
    @Timeout(value = 300)
    fun `discover offers incremental only for tables in the publication`() {
        val modes: Map<String, List<SyncMode>> =
            CliRunner.source("discover", spec).run().catalogs().single().streams.associate {
                it.name to it.supportedSyncModes
            }
        assertEquals(
            mapOf(
                PUBLISHED to listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                UNPUBLISHED to listOf(SyncMode.FULL_REFRESH),
            ),
            modes,
        )
    }

    companion object {
        const val PUBLISHED = "published"
        const val UNPUBLISHED = "unpublished"
        private val schema: String = TestAssetResourceNamer().getName()
        private val publication = "${schema.lowercase()}_publication"

        private lateinit var testdb: PostgresTestDatabase
        private lateinit var spec: PostgresSourceConfigurationSpecification
        private lateinit var connectionFactory: JdbcConnectionFactory

        fun execute(sql: String) {
            connectionFactory.get().use { conn ->
                conn.isReadOnly = false
                conn.autoCommit = true
                conn.createStatement().use { it.execute(sql) }
            }
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun setup() {
            testdb =
                PostgresTestDatabase.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_17,
                    PostgresTestDatabase.ContainerModifier.CONF,
                )
            spec =
                PostgresSourceFieldTypeMapperTest.config(testdb.container, listOf(schema)).apply {
                    setIncrementalConfigurationSpecificationValue(
                        CdcReplicationMethodConfigurationSpecification().also {
                            it.replicationSlot = "${schema.lowercase()}_slot"
                            it.publication = publication
                        },
                    )
                }
            connectionFactory =
                JdbcConnectionFactory(PostgresSourceConfigurationFactory().make(spec))
            execute("CREATE SCHEMA \"$schema\"")
            for (table in listOf(PUBLISHED, UNPUBLISHED)) {
                execute("CREATE TABLE \"$schema\".$table (id bigint PRIMARY KEY, v text)")
            }
            execute("CREATE PUBLICATION $publication FOR TABLE \"$schema\".$PUBLISHED")
        }
    }
}
