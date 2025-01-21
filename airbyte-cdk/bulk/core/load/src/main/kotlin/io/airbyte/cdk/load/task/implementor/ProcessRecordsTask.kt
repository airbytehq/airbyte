/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.DestinationStreamComplete
import io.airbyte.cdk.load.message.DestinationStreamIncomplete
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessRecordsTask : StreamLevel, ImplementorScope

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
    private val file: SpilledRawMessagesLocalFile,
    private val deserializer: Deserializer<DestinationMessage>,
    private val syncManager: SyncManager,
) : ProcessRecordsTask {
    override suspend fun execute() {
        val log = KotlinLogging.logger {}

        log.info { "Fetching stream loader for ${stream.descriptor}" }
        val streamLoader = syncManager.getOrAwaitStreamLoader(stream.descriptor)

        log.info { "Processing records from $file" }
        val batch =
            try {
                file.localFile.toFileReader().use { reader ->
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
                    streamLoader.processRecords(records, file.totalSizeBytes)
                }
            } finally {
                log.info { "Processing completed, deleting $file" }
                file.localFile.delete()
            }

        val wrapped = BatchEnvelope(batch, file.indexRange)
        taskLauncher.handleNewBatch(stream, wrapped)
    }
}

interface ProcessRecordsTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream,
        file: SpilledRawMessagesLocalFile,
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
        file: SpilledRawMessagesLocalFile,
    ): ProcessRecordsTask {
        return DefaultProcessRecordsTask(stream, taskLauncher, file, deserializer, syncManager)
    }
}
