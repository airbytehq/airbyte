/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.Stream
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

/**
 * Verifies that [MsSqlServerDebeziumOperations.buildMessageKeyColumns] skips streams whose name or
 * namespace contain characters Debezium's `message.key.columns` regex rejects (whitespace or `:`).
 *
 * Debezium validates each entry against `^\s*([^\s:]+):([^:\s]+)\s*$` and there is no quoting
 * mechanism for whitespace in this property. Including such entries causes the entire CDC sync to
 * fail at Debezium engine startup before any records are read. Skipping the override for those
 * streams lets Debezium fall back to its native primary key auto-detection from SQL Server system
 * tables.
 *
 * See: https://github.com/airbytehq/airbyte/issues/77729
 */
class MsSqlServerDebeziumOperationsMessageKeyColumnsTest {

    private fun stream(
        name: String,
        namespace: String?,
        primaryKey: List<EmittedField>? = listOf(EmittedField("id", IntFieldType)),
    ): Stream =
        Stream(
            id =
                StreamIdentifier.from(
                    StreamDescriptor().withName(name).withNamespace(namespace),
                ),
            schema = setOf(EmittedField("id", IntFieldType)),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = primaryKey,
            configuredCursor = null,
        )

    @Test
    fun `valid stream is included in output`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Users", namespace = "dbo")),
            )
        assertEquals("dbo.Users:id", result)
    }

    @Test
    fun `stream with whitespace in name is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Customer Orders", namespace = "dbo")),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream with whitespace in namespace is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Location", namespace = "Company Inc")),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream with colon in name is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Foo:Bar", namespace = "dbo")),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream with colon in namespace is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Users", namespace = "schema:weird")),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream with tab in name is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "User\tTable", namespace = "dbo")),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream without primary key is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "Users", namespace = "dbo", primaryKey = null)),
            )
        assertEquals("", result)
    }

    @Test
    fun `stream with empty primary key is skipped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(
                    stream(name = "Users", namespace = "dbo", primaryKey = emptyList()),
                ),
            )
        assertEquals("", result)
    }

    @Test
    fun `mix of valid and invalid streams keeps only valid ones joined by semicolon`() {
        val streams =
            listOf(
                stream(name = "Users", namespace = "dbo"),
                stream(
                    name = "Company Inc\$Location\$437dbf0e-84ff-417a-965d-ed2bb9650972",
                    namespace = "dbo",
                ),
                stream(
                    name = "Orders",
                    namespace = "dbo",
                    primaryKey =
                        listOf(
                            EmittedField("order_id", IntFieldType),
                            EmittedField("customer_id", IntFieldType),
                        ),
                ),
                stream(name = "WithColon", namespace = "weird:schema"),
            )
        val result = MsSqlServerDebeziumOperations.buildMessageKeyColumns(streams)
        assertEquals("dbo.Users:id;dbo.Orders:order_id,customer_id", result)
    }

    @Test
    fun `all-invalid stream set returns empty string so message_key_columns is omitted`() {
        val streams =
            listOf(
                stream(name = "Customer Orders", namespace = "dbo"),
                stream(name = "Location", namespace = "Company Inc"),
                stream(name = "WithColon", namespace = "weird:schema"),
            )
        val result = MsSqlServerDebeziumOperations.buildMessageKeyColumns(streams)
        assertEquals("", result)
    }

    @Test
    fun `multiple valid streams are joined by semicolon`() {
        val streams =
            listOf(
                stream(name = "Users", namespace = "dbo"),
                stream(
                    name = "Orders",
                    namespace = "sales",
                    primaryKey =
                        listOf(
                            EmittedField("order_id", IntFieldType),
                            EmittedField("customer_id", IntFieldType),
                        ),
                ),
            )
        val result = MsSqlServerDebeziumOperations.buildMessageKeyColumns(streams)
        assertEquals("dbo.Users:id;sales.Orders:order_id,customer_id", result)
    }

    @Test
    fun `empty stream list returns empty string`() {
        assertEquals("", MsSqlServerDebeziumOperations.buildMessageKeyColumns(emptyList()))
    }

    @Test
    fun `dots in identifier names are escaped`() {
        val result =
            MsSqlServerDebeziumOperations.buildMessageKeyColumns(
                listOf(stream(name = "users.archive", namespace = "dbo")),
            )
        assertEquals("dbo.users\\.archive:id", result)
    }
}
