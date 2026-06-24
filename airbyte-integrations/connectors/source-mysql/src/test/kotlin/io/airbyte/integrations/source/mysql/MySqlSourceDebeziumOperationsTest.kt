/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.time.Duration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class MySqlSourceDebeziumOperationsTest {

    @Test
    fun testGenerateWarmStartPropertiesStoresDdlOnlyForCapturedTables() {
        val properties =
            operations().generateWarmStartProperties(listOf(stream("test", "selected")))

        assertEquals(
            "true",
            properties[
                MySqlSourceDebeziumOperations.SCHEMA_HISTORY_STORE_ONLY_CAPTURED_TABLES_DDL_PROPERTY
            ]
        )
        assertEquals("""\Qtest.selected\E""", properties["table.include.list"])
    }

    @Test
    fun testGenerateColdStartPropertiesDoesNotStoreDdlOnlyForCapturedTables() {
        val properties =
            operations().generateColdStartProperties(listOf(stream("test", "selected")))

        assertFalse(
            properties.containsKey(
                MySqlSourceDebeziumOperations.SCHEMA_HISTORY_STORE_ONLY_CAPTURED_TABLES_DDL_PROPERTY
            )
        )
        assertFalse(properties.containsKey("table.include.list"))
        assertEquals("recovery", properties["snapshot.mode"])
    }

    private fun operations(): MySqlSourceDebeziumOperations {
        val configuration =
            MySqlSourceConfiguration(
                realHost = "localhost",
                realPort = 3306,
                sshTunnel = SshNoTunnelMethod,
                sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
                jdbcUrlFmt = "jdbc:mysql://%s:%d",
                jdbcProperties = mapOf("user" to "user"),
                namespaces = setOf("test"),
                tableFilters = emptyList(),
                incrementalConfiguration =
                    CdcIncrementalConfiguration(
                        initialLoadTimeout = Duration.ofHours(8),
                        serverTimezone = null,
                        invalidCdcCursorPositionBehavior =
                            InvalidCdcCursorPositionBehavior.RESET_SYNC,
                    ),
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofSeconds(5),
                checkPrivileges = true,
                treatTinyint1AsInteger = false,
            )
        return MySqlSourceDebeziumOperations(JdbcConnectionFactory(configuration), configuration)
    }

    private fun stream(namespace: String, name: String): Stream {
        val id = Field("id", IntFieldType)
        return Stream(
            id = StreamIdentifier.from(StreamDescriptor().withNamespace(namespace).withName(name)),
            schema = setOf(id),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = listOf(id),
            configuredCursor = id,
        )
    }
}
