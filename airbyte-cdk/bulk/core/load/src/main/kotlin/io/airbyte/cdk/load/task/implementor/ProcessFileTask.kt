/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileDomainMessage
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.LimitedMessageQueue
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.message.UnlimitedMessageQueue
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.task.SyncLevel
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton

interface ProcessFileTask : SyncLevel, KillableScope

class DefaultProcessFileTask(
    private val taskLauncher: DestinationTaskLauncher,
    private val syncManager: SyncManager,
    private val fileTransferQueue: MessageQueue<FileTransferQueueMessage>,
) : ProcessFileTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {

        fileTransferQueue.consume().collect {
            when (it.file) {
                is DestinationFile -> {
                    val (streamDescriptor, file) = it
                    log.info { "Fetching stream loader for $streamDescriptor and message $file" }
                    val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)

                    val fileMessage: DestinationFile = it.file
                    val batch = streamLoader.processFile(fileMessage)

                    val wrapped = BatchEnvelope(batch, Range.singleton(it.index!!))
                    taskLauncher.handleNewBatch(streamDescriptor, wrapped)

                }

                is DestinationFileStreamComplete -> {
                    val envelope = BatchEnvelope(SimpleBatch(Batch.State.COMPLETE))
                    taskLauncher.handleNewBatch(it.streamDescriptor, envelope)
                }
                is DestinationFileStreamIncomplete -> TODO()
            }

        }
    }
}

data class FileTransferQueueMessage(
    val streamDescriptor: DestinationStream.Descriptor,
    val file: DestinationFileDomainMessage,
    val index: Long? = null,
)

interface ProcessFileTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessFileTask
}

@Singleton
@Secondary
class DefaultFileRecordsTaskFactory(
    private val syncManager: SyncManager,
    @Named("transferFileQueue")
    private val fileTransferQueue: UnlimitedMessageQueue<FileTransferQueueMessage>,
) : ProcessFileTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessFileTask {
        return DefaultProcessFileTask(
            taskLauncher,
            syncManager,
            fileTransferQueue
        )
    }
}
