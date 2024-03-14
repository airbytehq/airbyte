/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import java.time.Clock
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class TimeTriggerTest {
    private val NOW_MS = System.currentTimeMillis()
    private val ONE_SEC = 1000L
    private val FIVE_MIN = (5 * 60 * 1000).toLong()

    @Test
    internal fun testTimeTrigger() {
        val bufferDequeue =
            Mockito.mock(
                BufferDequeue::class.java,
            )
        val flusher = Mockito.mock(DestinationFlushFunction::class.java)
        val runningFlushWorkers =
            Mockito.mock(
                RunningFlushWorkers::class.java,
            )

        val mockedNowProvider = Mockito.mock(Clock::class.java)
        Mockito.`when`(mockedNowProvider.millis()).thenReturn(NOW_MS)

        val detect =
            DetectStreamToFlush(
                bufferDequeue,
                runningFlushWorkers,
                AtomicBoolean(false),
                flusher,
                mockedNowProvider,
            )
        Assertions.assertEquals(false, detect.isTimeTriggered(NOW_MS).getLeft())
        Assertions.assertEquals(false, detect.isTimeTriggered(NOW_MS - ONE_SEC).getLeft())
        Assertions.assertEquals(true, detect.isTimeTriggered(NOW_MS - FIVE_MIN).getLeft())
    }
}
