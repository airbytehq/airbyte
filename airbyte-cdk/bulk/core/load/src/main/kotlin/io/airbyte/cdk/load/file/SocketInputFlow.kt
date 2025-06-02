/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.Ignored
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

class SocketInputFlow(
    private val catalog: DestinationCatalog,
    private val socket: ClientSocket,
    private val inputFormatReader: DataChannelReader,
    private val pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter,
    private val memoryManager: ReservationManager,
) : Flow<PipelineInputEvent> {
    private val log = KotlinLogging.logger {}

    override suspend fun collect(collector: FlowCollector<PipelineInputEvent>) {
        pipelineEventBookkeepingRouter.use {
            socket.connect { inputStream ->
                val unopenedStreams = catalog.streams.map { it.descriptor }.toMutableSet()
                inputFormatReader.read(inputStream).forEach { message ->
                    when (message) {
                        is DestinationStreamAffinedMessage -> {
                            val event =
                                pipelineEventBookkeepingRouter.handleStreamMessage(
                                    message,
                                    unopenedStreams = unopenedStreams
                                )
                            collector.emit(event)
                        }
                        is CheckpointMessage ->
                            pipelineEventBookkeepingRouter.handleCheckpoint(
                                memoryManager.reserve(message.serializedSizeBytes, message)
                            )
                        Undefined -> log.warn { "Unhandled message: $message" }
                        Ignored -> { /* do nothing */ }
                    }
                }
            }
        }
    }
}
