/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.finalization

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.mockk.every
import io.mockk.mockk
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.ValueSource

class StreamCompletionTrackerTest {

    @ParameterizedTest
    @ValueSource(ints = [1, 2, 3, 4, 10, 42, 99, 1000])
    fun `#allStreamsComplete should return true when all streams received`(size: Int) {
        // Given
        val catalog = Fixtures.catalog(size)
        val tracker = StreamCompletionTracker(catalog)

        // When
        repeat(size) { tracker.accept(Fixtures.streamCompleteMsg) }

        // Then
        assertTrue(tracker.allStreamsComplete())
    }

    @ParameterizedTest
    @CsvSource("1,0", "2, 1", "3, 2", "4, 3", "10, 8", "42, 41", "99, 50", "1001, 1000")
    fun `#allStreamsComplete should return false when all completes weren't received`(
        size: Int,
        received: Int,
    ) {
        // Given
        val catalog = Fixtures.catalog(size)
        val tracker = StreamCompletionTracker(catalog)

        // When
        repeat(received) { tracker.accept(Fixtures.streamCompleteMsg) }

        // Then
        assertFalse(tracker.allStreamsComplete()) // 2 out of 4 streams complete
    }

    object Fixtures {
        fun catalog(size: Int) = mockk<DestinationCatalog> { every { size() } returns size }

        val streamCompleteMsg = mockk<DestinationRecordStreamComplete>()
    }
}
