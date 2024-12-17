/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.util.lineSequence
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream
import kotlin.io.path.inputStream

interface ProcessRecordsTask : KillableScope

/**
 * Wraps @[StreamLoader.processRecords] and feeds it a lazy iterator over the last batch of spooled
 * records. On completion it rewraps the processed batch in the old envelope and kicks off batch
 * handling and/or close stream tasks.
 *
 * TODO: The batch handling logic here is identical to that in @[ProcessBatchTask]. Both should be
 * moved to the task launcher.
 */
class DefaultProcessRecordsTask(
    private val taskLauncher: DestinationTaskLauncher,
    private val deserializer: Deserializer<DestinationMessage>,
    private val syncManager: SyncManager,
    private val diskManager: ReservationManager,
    private val inputQueue: MessageQueue<FileAggregateMessage>,
    private val outputQueue: MultiProducerChannel<BatchEnvelope<*>>
) : ProcessRecordsTask {
    private val log = KotlinLogging.logger {}
    override suspend fun execute() {
        outputQueue.use {
            inputQueue.consume().collect { (streamDescriptor, file) ->
                log.info { "Fetching stream loader for $streamDescriptor" }
                val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)
                log.info { "Processing records from $file for stream $streamDescriptor" }
                val batch =
                    try {
                        file.localFile.inputStream().use { inputStream ->
                            val records = inputStream.toRecordIterator()
                            val batch = streamLoader.processRecords(records, file.totalSizeBytes)
                            log.info { "Finished processing $file" }
                            batch
                        }
                    } finally {
                        log.info { "Processing completed, deleting $file" }
                        file.localFile.toFile().delete()
                        diskManager.release(file.totalSizeBytes)
                    }

                val wrapped = BatchEnvelope(batch, file.indexRange, streamDescriptor)
                log.info { "Updating batch $wrapped for $streamDescriptor" }
                taskLauncher.handleNewBatch(streamDescriptor, wrapped)
                if (batch.requiresProcessing) {
                    outputQueue.publish(wrapped)
                } else {
                    log.info { "Batch $wrapped requires no further processing." }
                }
            }
        }
    }

    private fun InputStream.toRecordIterator(): Iterator<DestinationRecord> {
        return lineSequence()
            .map {
                when (val message = deserializer.deserialize(it)) {
                    is DestinationStreamAffinedMessage -> message
                    else ->
                        throw IllegalStateException(
                            "Expected record message, got ${message::class}"
                        )
                }
            }
            .takeWhile {
                it !is DestinationRecordStreamComplete && it !is DestinationRecordStreamIncomplete
            }
            .map { it as DestinationRecord }
            .iterator()
    }
}

interface ProcessRecordsTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessRecordsTask
}

data class FileAggregateMessage(
    val streamDescriptor: DestinationStream.Descriptor,
    val file: SpilledRawMessagesLocalFile
)

@Singleton
@Secondary
class DefaultProcessRecordsTaskFactory(
    private val deserializer: Deserializer<DestinationMessage>,
    private val syncManager: SyncManager,
    @Named("diskManager") private val diskManager: ReservationManager,
    @Named("fileAggregateQueue") private val inputQueue: MessageQueue<FileAggregateMessage>,
    @Named("batchQueue") private val outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
) : ProcessRecordsTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
    ): ProcessRecordsTask {
        return DefaultProcessRecordsTask(
            taskLauncher,
            deserializer,
            syncManager,
            diskManager,
            inputQueue,
            outputQueue,
        )
    }
}
