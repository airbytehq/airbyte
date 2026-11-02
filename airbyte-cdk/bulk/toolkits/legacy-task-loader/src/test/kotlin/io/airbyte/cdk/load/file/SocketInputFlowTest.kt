/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.util.UUID
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class SocketInputFlowTest {
    private fun stream(name: String) =
        DestinationStream(
            unmappedNamespace = "ns",
            unmappedName = name,
            mockk(),
            mockk(),
            1,
            1,
            1,
            namespaceMapper = NamespaceMapper(),
        )

    private val elsewhere = stream("elsewhere")
    private val here = stream("here")

    private fun record(stream: DestinationStream) =
        DestinationRecord(
            stream = stream,
            message = mockk(relaxed = true),
            serializedSizeBytes = 1L,
            checkpointId = null,
            airbyteRawId = UUID.randomUUID(),
        )

    /** What each event shows of itself: its type and stream(s). */
    private fun describe(event: PipelineInputEvent): String =
        when (event) {
            is PipelineMessage -> "record ${event.key.stream.name}"
            is PipelineHeartbeat -> "heartbeat ${event.completedStreams.map { it.name }.sorted()}"
            is PipelineEndOfStream -> "end-of-stream ${event.stream.name}"
        }

    /**
     * Reads [messages] from one socket. Before each message the router has seen the completions in
     * [completedBefore] at the same index, on any socket.
     */
    private suspend fun read(
        messages: List<DestinationMessage>,
        completedBefore: List<Set<DestinationStream>>,
    ): List<String> {
        val catalog = mockk<DestinationCatalog>()
        every { catalog.streams } returns listOf(elsewhere, here)

        var index = -1
        val router = mockk<PipelineEventBookkeepingRouter>(relaxed = true)
        every { router.completionCount } answers { completedBefore[index].size }
        every { router.completedStreams() } answers
            {
                completedBefore[index].map { it.mappedDescriptor }.toSet()
            }
        coEvery { router.handleStreamMessage(any(), any()) } answers
            {
                when (val message = firstArg<DestinationStreamAffinedMessage>()) {
                    is DestinationRecordStreamComplete ->
                        PipelineEndOfStream(message.stream.mappedDescriptor)
                    else ->
                        PipelineMessage(
                            emptyMap(),
                            StreamKey(message.stream.mappedDescriptor),
                            mockk(),
                        )
                }
            }

        val socket = mockk<ClientSocket>()
        every { socket.socketPath } returns "socket"
        coEvery { socket.connect(any()) } coAnswers
            {
                firstArg<suspend (InputStream) -> Unit>().invoke(ByteArrayInputStream(ByteArray(0)))
            }
        val reader =
            object : DataChannelReader {
                override fun read(inputStream: InputStream): Sequence<DestinationMessage> =
                    messages.asSequence().onEach { index++ }
            }

        return SocketInputFlow(catalog, socket, reader, router, mockk()).toList().map(::describe)
    }

    @Test
    fun `a stream completed on another socket is finished here at the next message`() = runTest {
        val events =
            read(
                listOf(record(elsewhere), record(here), record(here)),
                listOf(emptySet(), setOf(elsewhere), setOf(elsewhere)),
            )

        assertEquals(
            listOf(
                "record elsewhere",
                "heartbeat [elsewhere]",
                "record here",
                "record here",
                // The stream ends here at EOF as before: this socket never saw its COMPLETE.
                "end-of-stream elsewhere",
                "end-of-stream here",
            ),
            events,
        )
    }

    @Test
    fun `a stream completed on this socket is not in the heartbeat`() = runTest {
        val events =
            read(
                listOf(
                    record(here),
                    DestinationRecordStreamComplete(here, 0L),
                    record(elsewhere),
                    record(elsewhere),
                ),
                listOf(emptySet(), emptySet(), setOf(here), setOf(here, elsewhere)),
            )

        assertEquals(
            listOf(
                "record here",
                "end-of-stream here",
                "record elsewhere",
                "heartbeat [elsewhere]",
                "record elsewhere",
                "end-of-stream elsewhere",
            ),
            events,
        )
    }
}
