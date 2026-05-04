/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceOperations
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class JdbcAirbyteStreamFactoryTest {

    private lateinit var config: SourceConfiguration
    private lateinit var streamId: StreamIdentifier
    private lateinit var discoveredStream: DiscoveredStream

    @BeforeEach
    fun setUp() {
        config = mock(SourceConfiguration::class.java)
        streamId = mock(StreamIdentifier::class.java)
        discoveredStream = mock(DiscoveredStream::class.java)
        `when`(streamId.name).thenReturn("test_stream")
        `when`(streamId.namespace).thenReturn("test_namespace")
        `when`(discoveredStream.id).thenReturn(streamId)
        `when`(discoveredStream.columns)
            .thenReturn(
                listOf(
                    EmittedField("id", BigIntegerFieldType),
                    EmittedField("name", StringFieldType)
                )
            )
    }

    @Test
    fun testCreate_withCdcAndWithPK() {
        `when`(config.isCdc()).thenReturn(true)
        `when`(discoveredStream.primaryKeyColumnIDs).thenReturn(listOf(listOf("id")))

        val factory = H2SourceOperations()
        val stream = factory.create(config, discoveredStream)

        Assertions.assertEquals(
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            stream.supportedSyncModes
        )
        Assertions.assertTrue(stream.sourceDefinedCursor)
        Assertions.assertTrue(stream.isResumable)
        assertHasCdcMetaFields(stream)
        Assertions.assertEquals(
            listOf(H2SourceOperations.H2GlobalCursor.id),
            stream.defaultCursorField
        )
    }

    @Test
    fun testCreate_withCdcAndWithoutPK() {
        `when`(config.isCdc()).thenReturn(true)
        `when`(discoveredStream.primaryKeyColumnIDs).thenReturn(emptyList())

        val factory = H2SourceOperations()
        val stream = factory.create(config, discoveredStream)

        Assertions.assertEquals(listOf(SyncMode.FULL_REFRESH), stream.supportedSyncModes)
        Assertions.assertFalse(stream.sourceDefinedCursor)
        Assertions.assertFalse(stream.isResumable)
        // CDC streams without a primary key must still expose the CDC meta fields in their
        // schema; otherwise destinations whose catalog references the CDC cursor field reject it.
        assertHasCdcMetaFields(stream)
        Assertions.assertEquals(
            listOf(H2SourceOperations.H2GlobalCursor.id),
            stream.defaultCursorField
        )
    }

    @Test
    fun testCreate_withNonCdcAndWithPK() {
        `when`(config.isCdc()).thenReturn(false)
        `when`(discoveredStream.primaryKeyColumnIDs).thenReturn(listOf(listOf("id")))

        val factory = H2SourceOperations()
        val stream = factory.create(config, discoveredStream)

        Assertions.assertEquals(
            listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
            stream.supportedSyncModes
        )
        Assertions.assertFalse(stream.sourceDefinedCursor)
        Assertions.assertTrue(stream.isResumable)
        assertDoesNotHaveCdcMetaFields(stream)
    }

    @Test
    fun testCreate_withNonCdcAndWithoutPK() {
        `when`(config.isCdc()).thenReturn(false)
        `when`(discoveredStream.primaryKeyColumnIDs).thenReturn(emptyList())
        `when`(discoveredStream.columns)
            .thenReturn(listOf(EmittedField("non_cursor_col", BooleanFieldType)))

        val factory = H2SourceOperations()
        val stream = factory.create(config, discoveredStream)

        Assertions.assertEquals(listOf(SyncMode.FULL_REFRESH), stream.supportedSyncModes)
        Assertions.assertFalse(stream.sourceDefinedCursor)
        Assertions.assertFalse(stream.isResumable)
        assertDoesNotHaveCdcMetaFields(stream)
    }

    private fun assertHasCdcMetaFields(stream: AirbyteStream) {
        val properties = stream.jsonSchema["properties"] as ObjectNode
        for (metaField in H2SourceOperations().globalMetaFields) {
            Assertions.assertTrue(
                properties.has(metaField.id),
                "expected schema properties to contain ${metaField.id} but got ${properties.fieldNames().asSequence().toList()}",
            )
        }
    }

    private fun assertDoesNotHaveCdcMetaFields(stream: AirbyteStream) {
        val properties = stream.jsonSchema["properties"] as ObjectNode
        for (metaField in H2SourceOperations().globalMetaFields) {
            Assertions.assertFalse(
                properties.has(metaField.id),
                "did not expect schema properties to contain ${metaField.id}",
            )
        }
    }
}
