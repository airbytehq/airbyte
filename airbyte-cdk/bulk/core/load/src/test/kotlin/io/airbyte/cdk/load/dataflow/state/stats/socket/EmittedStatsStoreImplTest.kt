/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.socket

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class EmittedStatsStoreImplTest {

    @MockK private lateinit var catalog: DestinationCatalog

    private lateinit var store: EmittedStatsStoreImpl

    @BeforeEach
    fun setup() {
        store = EmittedStatsStoreImpl(catalog)
    }

    @Test
    fun `increment should add counts and bytes for a stream`() {
        // Given
        val descriptor = DestinationStream.Descriptor("namespace1", "stream1")

        // When
        store.increment(descriptor, 10L, 1000L)

        // Then
        val stats = store.get(descriptor)
        assertEquals(10L, stats.count)
        assertEquals(1000L, stats.bytes)
    }

    @Test
    fun `increment should accumulate multiple increments for the same stream`() {
        // Given
        val descriptor = DestinationStream.Descriptor("namespace1", "stream1")

        // When
        store.increment(descriptor, 10L, 1000L)
        store.increment(descriptor, 5L, 500L)
        store.increment(descriptor, 15L, 1500L)

        // Then
        val stats = store.get(descriptor)
        assertEquals(30L, stats.count)
        assertEquals(3000L, stats.bytes)
    }

    @Test
    fun `increment should track multiple streams independently`() {
        // Given
        val descriptor1 = DestinationStream.Descriptor("namespace1", "stream1")
        val descriptor2 = DestinationStream.Descriptor("namespace2", "stream2")
        val descriptor3 = DestinationStream.Descriptor(null, "stream3")

        // When
        store.increment(descriptor1, 10L, 1000L)
        store.increment(descriptor2, 20L, 2000L)
        store.increment(descriptor3, 30L, 3000L)

        // Then
        assertEquals(10L, store.get(descriptor1).count)
        assertEquals(1000L, store.get(descriptor1).bytes)

        assertEquals(20L, store.get(descriptor2).count)
        assertEquals(2000L, store.get(descriptor2).bytes)

        assertEquals(30L, store.get(descriptor3).count)
        assertEquals(3000L, store.get(descriptor3).bytes)
    }

    @Test
    fun `get should return zero stats for untracked stream`() {
        // Given
        val descriptor = DestinationStream.Descriptor("namespace1", "stream1")

        // When
        val stats = store.get(descriptor)

        // Then
        assertEquals(0L, stats.count)
        assertEquals(0L, stats.bytes)
    }

    @Test
    fun `getStats should return empty list when no streams have stats`() {
        // Given
        val streams =
            listOf(
                Fixtures.createStream("namespace1", "stream1"),
                Fixtures.createStream("namespace2", "stream2"),
            )
        every { catalog.streams } returns streams

        // When
        val messages = store.getStats()

        // Then
        assertTrue(messages.isEmpty())
    }

    @Test
    fun `getStats should return messages only for streams with non-zero counts`() {
        // Given
        val stream1 = Fixtures.createStream("namespace1", "stream1")
        val stream2 = Fixtures.createStream("namespace2", "stream2")
        val stream3 = Fixtures.createStream("namespace3", "stream3")

        every { catalog.streams } returns listOf(stream1, stream2, stream3)

        store.increment(stream1.unmappedDescriptor, 10L, 1000L)
        store.increment(stream3.unmappedDescriptor, 30L, 3000L)
        // stream2 has no increments

        // When
        val messages = store.getStats()

        // Then
        assertEquals(2, messages.size)

        val message1 = messages.find { it.record.stream == "stream1" }
        assertNotNull(message1)
        assertEquals("namespace1", message1?.record?.namespace)
        assertEquals(10L, message1?.record?.additionalProperties?.get("emittedRecordsCount"))
        assertEquals(1000L, message1?.record?.additionalProperties?.get("emittedBytesCount"))

        val message3 = messages.find { it.record.stream == "stream3" }
        assertNotNull(message3)
        assertEquals("namespace3", message3?.record?.namespace)
        assertEquals(30L, message3?.record?.additionalProperties?.get("emittedRecordsCount"))
        assertEquals(3000L, message3?.record?.additionalProperties?.get("emittedBytesCount"))
    }

    @Test
    fun `buildMessage should create proper AirbyteMessage with stats`() {
        // Given
        val descriptor = DestinationStream.Descriptor("test-namespace", "test-stream")
        val stats = EmissionStats(count = 42L, bytes = 4200L)

        // When
        val message = store.buildMessage(descriptor, stats)

        // Then
        assertEquals(AirbyteMessage.Type.RECORD, message.type)
        assertEquals("test-namespace", message.record.namespace)
        assertEquals("test-stream", message.record.stream)
        assertEquals(Jsons.emptyObject(), message.record.data)
        assertEquals(
            true,
            message.record.additionalProperties[OutputConsumer.IS_DUMMY_STATS_MESSAGE],
        )
        assertEquals(42L, message.record.additionalProperties["emittedRecordsCount"])
        assertEquals(4200L, message.record.additionalProperties["emittedBytesCount"])
    }

    @Test
    fun `buildMessage should handle null namespace`() {
        // Given
        val descriptor = DestinationStream.Descriptor(null, "test-stream")
        val stats = EmissionStats(count = 100L, bytes = 10000L)

        // When
        val message = store.buildMessage(descriptor, stats)

        // Then
        assertEquals(AirbyteMessage.Type.RECORD, message.type)
        assertEquals(null, message.record.namespace)
        assertEquals("test-stream", message.record.stream)
        assertEquals(100L, message.record.additionalProperties["emittedRecordsCount"])
        assertEquals(10000L, message.record.additionalProperties["emittedBytesCount"])
    }

    @Test
    fun `getStats should work correctly with mixed increments`() {
        // Given
        val stream1 = Fixtures.createStream("namespace1", "stream1")
        val stream2 = Fixtures.createStream("namespace2", "stream2")

        every { catalog.streams } returns listOf(stream1, stream2)

        // Multiple increments for stream1
        store.increment(stream1.unmappedDescriptor, 5L, 500L)
        store.increment(stream1.unmappedDescriptor, 10L, 1000L)
        store.increment(stream1.unmappedDescriptor, 15L, 1500L)

        // Single increment for stream2
        store.increment(stream2.unmappedDescriptor, 20L, 2000L)

        // When
        val messages = store.getStats()

        // Then
        assertEquals(2, messages.size)

        val message1 = messages.find { it.record.stream == "stream1" }
        assertEquals(30L, message1?.record?.additionalProperties?.get("emittedRecordsCount"))
        assertEquals(3000L, message1?.record?.additionalProperties?.get("emittedBytesCount"))

        val message2 = messages.find { it.record.stream == "stream2" }
        assertEquals(20L, message2?.record?.additionalProperties?.get("emittedRecordsCount"))
        assertEquals(2000L, message2?.record?.additionalProperties?.get("emittedBytesCount"))
    }

    object Fixtures {
        private val namespaceMapper =
            mockk<NamespaceMapper> {
                every { map(any(), any()) } answers
                    {
                        DestinationStream.Descriptor(firstArg(), secondArg())
                    }
            }

        fun createStream(namespace: String?, name: String): DestinationStream {
            return DestinationStream(
                unmappedNamespace = namespace,
                unmappedName = name,
                importType = Append,
                schema = io.airbyte.cdk.load.data.ObjectType(linkedMapOf()),
                generationId = 1L,
                minimumGenerationId = 1L,
                syncId = 1L,
                namespaceMapper = namespaceMapper,
                tableSchema =
                    io.airbyte.cdk.load.schema.model.StreamTableSchema(
                        tableNames =
                            io.airbyte.cdk.load.schema.model.TableNames(
                                finalTableName =
                                    io.airbyte.cdk.load.schema.model.TableName(
                                        namespace ?: "default",
                                        name
                                    )
                            ),
                        columnSchema =
                            io.airbyte.cdk.load.schema.model.ColumnSchema(
                                inputSchema = mapOf(),
                                inputToFinalColumnNames = mapOf(),
                                finalSchema = mapOf(),
                            ),
                        importType = Append,
                    )
            )
        }
    }
}
