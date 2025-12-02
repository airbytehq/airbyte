/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class StreamCompletionTrackerTest {

    @Test
    fun `#allStreamsComplete should return true when all streams received DestinationRecordStreamComplete`() {
        // Given
        val streams =
            listOf(
                createStream("namespace1", "stream1"),
                createStream("namespace1", "stream2"),
                createStream("namespace2", "stream1")
            )
        val catalog = mockk<DestinationCatalog> { every { this@mockk.streams } returns streams }
        val tracker = StreamCompletionTracker(catalog)

        // When - send completion messages for all streams
        streams.forEach { stream ->
            val completeMsg =
                mockk<DestinationRecordStreamComplete> {
                    every { this@mockk.stream } returns stream
                }
            tracker.accept(completeMsg)
        }

        // Then
        assertTrue(tracker.allStreamsComplete())
    }

    @Test
    fun `#allStreamsComplete should return false when not all streams received completion`() {
        // Given
        val streams =
            listOf(
                createStream("namespace1", "stream1"),
                createStream("namespace1", "stream2"),
                createStream("namespace2", "stream1")
            )
        val catalog = mockk<DestinationCatalog> { every { this@mockk.streams } returns streams }
        val tracker = StreamCompletionTracker(catalog)

        // When - send completion for only 2 out of 3 streams
        val completeMsg1 =
            mockk<DestinationRecordStreamComplete> {
                every { this@mockk.stream } returns streams[0]
            }
        val completeMsg2 =
            mockk<DestinationRecordStreamComplete> {
                every { this@mockk.stream } returns streams[1]
            }

        tracker.accept(completeMsg1)
        tracker.accept(completeMsg2)
        // Not sending completion for streams[2]

        // Then
        assertFalse(tracker.allStreamsComplete())
    }

    @Test
    fun `#allStreamsComplete should return false when no streams received completion`() {
        // Given
        val streams =
            listOf(createStream("namespace1", "stream1"), createStream("namespace1", "stream2"))
        val catalog = mockk<DestinationCatalog> { every { this@mockk.streams } returns streams }
        val tracker = StreamCompletionTracker(catalog)

        // When - no completion messages sent

        // Then
        assertFalse(tracker.allStreamsComplete())
    }

    @Test
    fun `#allStreamsComplete should handle duplicate completion messages correctly`() {
        // Given
        val stream = createStream("namespace1", "stream1")
        val catalog =
            mockk<DestinationCatalog> { every { this@mockk.streams } returns listOf(stream) }
        val tracker = StreamCompletionTracker(catalog)

        // When - send multiple completion messages for the same stream
        val completeMsg1 =
            mockk<DestinationRecordStreamComplete> { every { this@mockk.stream } returns stream }
        val completeMsg2 =
            mockk<DestinationRecordStreamComplete> { every { this@mockk.stream } returns stream }

        tracker.accept(completeMsg1)
        tracker.accept(completeMsg2) // Duplicate for same stream

        // Then
        assertTrue(tracker.allStreamsComplete())
    }

    @Test
    fun `#allStreamsComplete should return true for empty catalog`() {
        // Given
        val catalog = mockk<DestinationCatalog> { every { this@mockk.streams } returns emptyList() }
        val tracker = StreamCompletionTracker(catalog)

        // When - no streams to complete

        // Then
        assertTrue(tracker.allStreamsComplete())
    }

    private fun createStream(namespace: String, name: String): DestinationStream {
        val descriptor = DestinationStream.Descriptor(namespace, name)
        return mockk<DestinationStream> { every { mappedDescriptor } returns descriptor }
    }
}
