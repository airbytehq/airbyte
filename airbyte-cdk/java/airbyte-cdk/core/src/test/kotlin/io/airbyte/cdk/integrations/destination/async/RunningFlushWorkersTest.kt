/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Optional
import java.util.UUID
import org.assertj.core.api.Assertions
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class RunningFlushWorkersTest {
    private val SIZE_10MB = (10 * 1024 * 1024).toLong()

    private val FLUSH_WORKER_ID1: UUID = UUID.randomUUID()
    private val FLUSH_WORKER_ID2: UUID = UUID.randomUUID()
    private val STREAM1: StreamDescriptor =
        StreamDescriptor()
            .withNamespace(
                "namespace1",
            )
            .withName("stream1")
    private val STREAM2: StreamDescriptor =
        StreamDescriptor()
            .withNamespace(
                "namespace2",
            )
            .withName("stream2")

    private lateinit var runningFlushWorkers: RunningFlushWorkers

    @BeforeEach
    internal fun setup() {
        runningFlushWorkers = RunningFlushWorkers()
    }

    @Test
    internal fun testTrackFlushWorker() {
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(0)
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(1)
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2)
        runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(2)
    }

    @Test
    internal fun testCompleteFlushWorker() {
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1)
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2)
        runningFlushWorkers.completeFlushWorker(STREAM1, FLUSH_WORKER_ID1)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(1)
        runningFlushWorkers.completeFlushWorker(STREAM1, FLUSH_WORKER_ID2)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(0)
    }

    @Test
    internal fun testCompleteFlushWorkerWithoutTrackThrowsException() {
        Assertions.assertThatThrownBy {
                runningFlushWorkers.completeFlushWorker(
                    STREAM1,
                    FLUSH_WORKER_ID1,
                )
            }
            .isInstanceOf(IllegalStateException::class.java)
            .hasMessageContaining("Cannot complete flush worker for stream that has not started.")
    }

    @Test
    internal fun testMultipleStreams() {
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1)
        runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1).size,
            )
            .isEqualTo(1)
        Assertions.assertThat(
                runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2).size,
            )
            .isEqualTo(1)
    }

    @Test
    internal fun testGetSizesOfRunningWorkerBatches() {
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID1)
        runningFlushWorkers.trackFlushWorker(STREAM1, FLUSH_WORKER_ID2)
        runningFlushWorkers.trackFlushWorker(STREAM2, FLUSH_WORKER_ID1)
        assertEquals(
            listOf(Optional.empty(), Optional.empty<Any>()),
            runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1),
        )
        assertEquals(
            listOf(Optional.empty<Any>()),
            runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2),
        )
        assertThrows(
            IllegalStateException::class.java,
        ) {
            runningFlushWorkers.registerBatchSize(
                STREAM2,
                FLUSH_WORKER_ID2,
                SIZE_10MB,
            )
        }
        runningFlushWorkers.registerBatchSize(STREAM1, FLUSH_WORKER_ID1, SIZE_10MB)
        runningFlushWorkers.registerBatchSize(STREAM1, FLUSH_WORKER_ID2, SIZE_10MB)
        runningFlushWorkers.registerBatchSize(STREAM2, FLUSH_WORKER_ID1, SIZE_10MB)
        assertEquals(
            listOf(Optional.of(SIZE_10MB), Optional.of(SIZE_10MB)),
            runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM1),
        )
        assertEquals(
            listOf(Optional.of(SIZE_10MB)),
            runningFlushWorkers.getSizesOfRunningWorkerBatches(STREAM2),
        )
    }
}
