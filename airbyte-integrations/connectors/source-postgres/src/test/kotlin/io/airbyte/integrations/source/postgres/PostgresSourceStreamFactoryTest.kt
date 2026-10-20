/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.airbyte.integrations.source.postgres.operations.PostgresSourceStreamFactory
import io.airbyte.integrations.source.postgres.operations.types.PostgresTimestampTzFieldType
import io.airbyte.integrations.source.postgres.operations.types.PostgresUuidFieldType
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.mockk.mockk
import java.time.Duration
import kotlin.time.Duration.Companion.seconds
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PostgresSourceStreamFactoryTest {
    private val config =
        PostgresSourceConfiguration(
            realHost = "localhost",
            realPort = 5432,
            sshTunnel = null,
            sshConnectionOptions =
                SshConnectionOptions(1.seconds, 2.seconds, kotlin.time.Duration.ZERO),
            jdbcUrlFmt = "jdbc:postgresql://%s:%d/",
            jdbcProperties = mapOf(),
            database = "db",
            namespaces = setOf("public"),
            incrementalConfiguration = UserDefinedCursorIncrementalConfiguration,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.ofMinutes(5),
            checkPrivileges = false,
        )

    // No namespace: the factory then skips its views lookup and never touches the connection.
    private val factory = PostgresSourceStreamFactory(mockk<JdbcConnectionFactory>())
    private val uuidColumn = EmittedField("user_id", PostgresUuidFieldType)
    private val timestampColumn = EmittedField("updated_at", PostgresTimestampTzFieldType)

    private fun discovered(vararg columns: EmittedField) =
        DiscoveredStream(
            StreamIdentifier.from(StreamDescriptor().withName("profiles")),
            columns.toList(),
            listOf(listOf(columns.first().id)),
        )

    @Test
    fun `uuid columns are not cursor candidates`() {
        assertFalse(factory.isPossibleCursor(uuidColumn))
        assertTrue(factory.isPossibleCursor(timestampColumn))
    }

    @Test
    fun `a table whose only candidate column is a uuid is full refresh only`() {
        val stream = factory.create(config, discovered(uuidColumn))
        assertEquals(listOf(SyncMode.FULL_REFRESH), stream.supportedSyncModes)
    }

    @Test
    fun `a uuid column next to a timestamp column keeps incremental`() {
        val stream = factory.create(config, discovered(uuidColumn, timestampColumn))
        assertEquals(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.supportedSyncModes)
    }
}
