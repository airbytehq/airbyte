/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.unmockkAll
import io.mockk.verify
import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

private class RecordingOutputConsumer(clock: Clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC)) :
    OutputConsumer(clock) {

    private val _messages = mutableListOf<AirbyteMessage>()
    val messages: List<AirbyteMessage>
        get() = _messages

    override fun accept(airbyteMessage: AirbyteMessage) {
        _messages += airbyteMessage
    }
    override fun close() = Unit
}

class StatsEmitterTest {

    private lateinit var syncManager: SyncManager
    private lateinit var streamManager: io.airbyte.cdk.load.state.StreamManager
    private lateinit var catalog: DestinationCatalog

    private lateinit var recordingConsumer: RecordingOutputConsumer
    private lateinit var dummyConsumer: DummyStatsMessageConsumer

    private lateinit var emitterJob: Job

    private val testDescriptor = DestinationStream.Descriptor("foo", "bar")
    private val testDelay = 10L

    @BeforeEach
    fun setUp() {
        streamManager =
            mockk(relaxed = true) {
                every { readCount() } returnsMany listOf(10L, 11L, 12L)
                every { byteCount() } returnsMany listOf(1_000L, 1_100L, 1_200L)
                every { receivedStreamComplete() } returnsMany listOf(false, false, true)
            }
        syncManager = mockk { every { getStreamManager(testDescriptor) } returns streamManager }

        val dstStream = mockk<DestinationStream>()
        every { dstStream.unmappedNamespace } returns "foo"
        every { dstStream.unmappedName } returns "bar"
        every { dstStream.descriptor } returns testDescriptor
        catalog = mockk { every { streams } returns listOf(dstStream) }

        recordingConsumer = RecordingOutputConsumer()
        dummyConsumer = DummyStatsMessageConsumer(recordingConsumer)
    }

    @AfterEach
    fun tearDown() {
        if (this::emitterJob.isInitialized) emitterJob.cancel()
        unmockkAll()
    }

    @Test
    fun `first message emitted immediately`() = runTest {
        val emitter = StatsEmitter(syncManager, catalog, dummyConsumer, testDelay)
        emitterJob = launch { emitter.execute() }

        delay(10)

        assertEquals(1, recordingConsumer.messages.size)

        val rec = recordingConsumer.messages.first().record
        assertEquals("foo", rec.namespace)
        assertEquals("bar", rec.stream)
        assertEquals(10L, rec.additionalProperties["emittedRecordsCount"])
        assertEquals(1_000L, rec.additionalProperties["emittedBytesCount"])

        emitterJob.cancelAndJoin()
    }

    @Test
    fun `emits once per period then stops after completion`() = runTest {
        val emitter = StatsEmitter(syncManager, catalog, dummyConsumer, testDelay)
        emitterJob = launch { emitter.execute() }

        delay(35)

        assertEquals(2, recordingConsumer.messages.size)

        val first = recordingConsumer.messages.first().record
        assertTrue(first.additionalProperties["emittedRecordsCount"] == 10L)
        assertTrue(first.additionalProperties["emittedBytesCount"] == 1000L)

        val second = recordingConsumer.messages.last().record
        assertTrue(second.additionalProperties["emittedRecordsCount"] == 11L)
        assertTrue(second.additionalProperties["emittedBytesCount"] == 1_100L)

        verify(exactly = 2) {
            streamManager.readCount()
            streamManager.byteCount()
        }
        verify(atLeast = 3) { streamManager.receivedStreamComplete() }

        emitterJob.cancelAndJoin()
    }
}
