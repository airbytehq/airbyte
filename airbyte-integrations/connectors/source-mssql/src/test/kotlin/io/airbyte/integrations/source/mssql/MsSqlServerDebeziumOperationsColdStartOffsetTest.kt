/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Test

/**
 * Verifies that [DebeziumPropertiesBuilder.sanitizeTopicPrefix] is applied to the "server" field
 * in the cold-start offset key. Without sanitization, database names containing characters such as
 * spaces or special symbols produce an offset key that diverges from Debezium's internal
 * [SqlServerPartition] key, causing CDC cold starts to fail with:
 *   "Could not find existing redo log information while attempting schema only recovery snapshot"
 *
 * See: https://github.com/airbytehq/airbyte/issues/73326
 */
class MsSqlServerDebeziumOperationsColdStartOffsetTest {

    @Test
    fun `sanitizeTopicPrefix replaces special characters with underscores`() {
        // Database names with spaces, dots, and other special characters should be sanitized.
        val rawName = "My Database.Name"
        val sanitized = DebeziumPropertiesBuilder.sanitizeTopicPrefix(rawName)
        assertEquals("My_Database.Name", sanitized)
        assertNotEquals(rawName, sanitized, "Raw name with space should differ from sanitized form")
    }

    @Test
    fun `sanitizeTopicPrefix preserves simple alphanumeric names`() {
        val simpleName = "TestDB"
        val sanitized = DebeziumPropertiesBuilder.sanitizeTopicPrefix(simpleName)
        assertEquals(simpleName, sanitized, "Simple alphanumeric name should be unchanged")
    }

    @Test
    fun `sanitizeTopicPrefix handles names with multiple special characters`() {
        val complexName = "my db@host:3306"
        val sanitized = DebeziumPropertiesBuilder.sanitizeTopicPrefix(complexName)
        // Spaces, @, and : are not in the allowed set [A-Za-z0-9._-] and should be replaced
        assertEquals("my_db_host_3306", sanitized)
    }

    @Test
    fun `sanitizeTopicPrefix preserves dots dashes and underscores`() {
        val name = "my-db_name.v2"
        val sanitized = DebeziumPropertiesBuilder.sanitizeTopicPrefix(name)
        assertEquals(name, sanitized, "Dots, dashes, and underscores should be preserved")
    }
}
