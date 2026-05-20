/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class MsSqlSourceOperationsTest {
    @Test
    @DisplayName(
        "CDC streams without primary keys should expose CDC fields and incremental append"
    )
    fun testCdcPkLessStreamSupportsIncrementalAppend() {
        val config = mock(SourceConfiguration::class.java)
        `when`(config.isCdc()).thenReturn(true)

        val discoveredStream =
            DiscoveredStream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withName("pkless_cdc_table").withNamespace("dbo")
                    ),
                columns =
                    listOf(
                        EmittedField("id", IntFieldType),
                        EmittedField("description", StringFieldType),
                    ),
                primaryKeyColumnIDs = emptyList(),
            )

        val stream = MsSqlSourceOperations().create(config, discoveredStream)

        assertEquals(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.supportedSyncModes)
        assertEquals(emptyList<List<String>>(), stream.sourceDefinedPrimaryKey)
        assertEquals(
            listOf(MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id),
            stream.defaultCursorField,
        )
        assertTrue(stream.sourceDefinedCursor)
        assertFalse(stream.isResumable)
        assertTrue(
            stream.jsonSchema["properties"].has(
                MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id
            )
        )
        assertTrue(stream.jsonSchema["properties"].has(CommonMetaField.CDC_UPDATED_AT.id))
        assertTrue(
            stream.jsonSchema["properties"].has(
                MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_LSN.id
            )
        )
    }
}
