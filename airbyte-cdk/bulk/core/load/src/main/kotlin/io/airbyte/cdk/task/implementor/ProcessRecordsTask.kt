/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task.implementor

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.message.DestinationStreamComplete
import io.airbyte.cdk.message.DestinationStreamIncomplete
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.task.DestinationTaskLauncher
import io.airbyte.cdk.task.ImplementorTask
import io.airbyte.cdk.task.StreamTask
import io.airbyte.cdk.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessRecordsTask : StreamTask, ImplementorTask

/**
 * Wraps @[StreamLoader.processRecords] and feeds it a lazy iterator over the last batch of spooled
 * records. On completion it rewraps the processed batch in the old envelope and kicks off batch
 * handling and/or close stream tasks.
 *
 * TODO: The batch handling logic here is identical to that in @[ProcessBatchTask]. Both should be
 * moved to the task launcher.
 */
class DefaultProcessRecordsTask(
    override val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher,
    private val fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    private val deserializer: Deserializer<DestinationMessage>,
    private val syncManager: SyncManager,
) : ProcessRecordsTask {
    override suspend fun execute() {
        val log = KotlinLogging.logger {}

        log.info { "Fetching stream loader for ${stream.descriptor}" }
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)

        log.info { "Processing records from ${fileEnvelope.batch.localFile}" }
        val nextBatch =
            try {
                fileEnvelope.batch.localFile.toFileReader().use { reader ->
                    val records =
                        reader
                            .lines()
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
                                it !is DestinationStreamComplete &&
                                    it !is DestinationStreamIncomplete
                            }
                            .map { it as DestinationRecord }
                            .iterator()
                    streamLoader.processRecords(records, fileEnvelope.batch.totalSizeBytes)
                }
            } finally {
                log.info { "Processing completed, deleting ${fileEnvelope.batch.localFile}" }
                fileEnvelope.batch.localFile.delete()
            }

        val wrapped = fileEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(stream, wrapped)
    }
}

interface ProcessRecordsTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask
}

@Singleton
@Secondary
class DefaultProcessRecordsTaskFactory(
    private val deserializer: Deserializer<DestinationMessage>,
    private val syncManager: SyncManager,
) : ProcessRecordsTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask {
        return DefaultProcessRecordsTask(
            stream,
            taskLauncher,
            fileEnvelope,
            deserializer,
            syncManager
        )
    }
}
