/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.FileTransferQueueEndOfStream
import io.airbyte.cdk.load.message.FileTransferQueueMessage
import io.airbyte.cdk.load.message.FileTransferQueueRecord
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.FilePartAccumulatorFactory
import io.airbyte.cdk.load.write.object_storage.FilePartAccumulatorLegacy
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class ProcessFileTaskLegacy(
    @Named("fileMessageQueue") private val inputQueue: MessageQueue<FileTransferQueueMessage>,
    @Named("objectLoaderPartQueue")
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val partAccumulatorFactory: FilePartAccumulatorFactory,
) : Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    val log = KotlinLogging.logger {}
    private val accumulators =
        ConcurrentHashMap<DestinationStream.Descriptor, FilePartAccumulatorLegacy>()

    override suspend fun execute() {
        inputQueue.consume().collect { message ->
            when (message) {
                is FileTransferQueueRecord -> {
                    val acc =
                        accumulators.getOrPut(message.stream.descriptor) {
                            partAccumulatorFactory.make(message.stream)
                        }
                    acc.handleFileMessage(
                        message.file,
                        message.index,
                        message.checkpointId,
                    )
                }
                is FileTransferQueueEndOfStream -> {
                    outputQueue.broadcast(PipelineEndOfStream(message.stream.descriptor))
                }
            }
        }
    }
}
