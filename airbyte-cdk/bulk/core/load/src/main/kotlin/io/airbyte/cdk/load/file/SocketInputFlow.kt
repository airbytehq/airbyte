/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.Ignored
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.ProbeMessage
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import org.apache.mina.util.ConcurrentHashSet

class SocketInputFlow(
    private val catalog: DestinationCatalog,
    private val socket: ClientSocket,
    private val inputFormatReader: DataChannelReader,
    private val pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter,
    private val memoryManager: ReservationManager,
    private val logPerNRecords: Long = 100_000L
) : Flow<PipelineInputEvent> {
    private val log = KotlinLogging.logger {}

    private val sawEndOfStream = ConcurrentHashSet<DestinationStream.Descriptor>()

    override suspend fun collect(collector: FlowCollector<PipelineInputEvent>) {
        pipelineEventBookkeepingRouter.use {
            socket.connect { inputStream ->
                val unopenedStreams = catalog.streams.map { it.descriptor }.toMutableSet()
                var messagesRead = 0L
                inputFormatReader.read(inputStream).forEach { message ->
                    messagesRead++
                    if (messagesRead % logPerNRecords == 0L) {
                        log.info { "Read $messagesRead messages from ${socket.socketPath}" }
                    }

                    when (message) {
                        is DestinationStreamAffinedMessage -> {
                            val event =
                                pipelineEventBookkeepingRouter.handleStreamMessage(
                                    message,
                                    unopenedStreams = unopenedStreams
                                )
                            if (event is PipelineEndOfStream) {
                                sawEndOfStream.add(event.stream)
                            }
                            collector.emit(event)
                        }
                        is CheckpointMessage ->
                            pipelineEventBookkeepingRouter.handleCheckpoint(
                                memoryManager.reserve(message.serializedSizeBytes, message)
                            )
                        is ProbeMessage -> collector.emit(PipelineHeartbeat())
                        Undefined -> log.warn { "Unhandled message: $message" }
                        Ignored -> {
                            /* do nothing */
                        }
                    }
                }
            }
            // Treat EOF as end-of-stream. (Source should send end-of-stream on every
            // socket, but currently does not.)
            catalog.streams.forEach {
                if (!sawEndOfStream.contains(it.descriptor)) {
                    log.info { "Emitting end-of-stream for ${it.descriptor}" }
                    collector.emit(PipelineEndOfStream(it.descriptor))
                }
            }
        }
    }
}
