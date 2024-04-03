/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.mockk.every
import io.mockk.mockk
import java.time.Clock
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class TimeTriggerTest {
    companion object {
        private val NOW_MS = System.currentTimeMillis()
        private const val ONE_SEC = 1000L
        private const val FIVE_MIN = (5 * 60 * 1000).toLong()
    }

    @Test
    internal fun testTimeTrigger() {
        val bufferDequeue: BufferDequeue = mockk()
        val flusher: DestinationFlushFunction = mockk()
        val runningFlushWorkers: RunningFlushWorkers = mockk()
        val mockedNowProvider: Clock = mockk()

        every { mockedNowProvider.millis() } returns NOW_MS

        val detect =
            DetectStreamToFlush(
                bufferDequeue = bufferDequeue,
                runningFlushWorkers = runningFlushWorkers,
                destinationFlushFunction = flusher,
                airbyteFileUtils = AirbyteFileUtils(),
                nowProvider = Optional.of(mockedNowProvider),
            )

        assertEquals(false, detect.isTimeTriggered(NOW_MS).first)
        assertEquals(false, detect.isTimeTriggered(NOW_MS - ONE_SEC).first)
        assertEquals(true, detect.isTimeTriggered(NOW_MS - FIVE_MIN).first)
    }
}
