/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.load.write.FileBatchAccumulator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class ProcessFileTask(
    private val syncManager: SyncManager,
    private val inputQueue: MessageQueue<FileTransferQueueMessage>,
    private val outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
) : Task() {
    override val terminalCondition: TerminalCondition = SelfTerminating

    val log = KotlinLogging.logger {}
    private val accumulators =
        ConcurrentHashMap<DestinationStream.Descriptor, FileBatchAccumulator>()

    override suspend fun execute() {
        outputQueue.use {
            inputQueue.consume().collect { (streamDescriptor, file, index) ->
                val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)

                val acc =
                    accumulators.getOrPut(streamDescriptor) {
                        streamLoader.createFileBatchAccumulator(outputQueue)
                    }

                acc.processFilePart(file, index)
            }
        }
    }
}

data class FileTransferQueueMessage(
    val streamDescriptor: DestinationStream.Descriptor,
    val file: DestinationFile,
    val index: Long,
)
