/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.message.DestinationStreamComplete
import io.airbyte.cdk.message.DestinationStreamIncomplete
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

interface ProcessRecordsTask : Task

/**
 * Wraps @[StreamLoader.processRecords] and feeds it a lazy iterator over the last batch of spooled
 * records. On completion it rewraps the processed batch in the old envelope and kicks off batch
 * handling and/or close stream tasks.
 *
 * TODO: The batch handling logic here is identical to that in @[ProcessBatchTask]. Both should be
 * moved to the task launcher.
 */
class DefaultProcessRecordsTask(
    private val streamLoader: StreamLoader,
    private val taskLauncher: DestinationTaskLauncher,
    private val fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    private val deserializer: Deserializer<DestinationMessage>,
) : ProcessRecordsTask {
    override suspend fun execute() {
        val log = KotlinLogging.logger {}

        log.info { "Processing records from ${fileEnvelope.batch.localFile}" }
        val nextBatch =
            try {
                withContext(Dispatchers.IO) {
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
                }
            } finally {
                log.info { "Processing completed, deleting ${fileEnvelope.batch.localFile}" }
                fileEnvelope.batch.localFile.delete()
            }

        val wrapped = fileEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(streamLoader, wrapped)
    }
}

interface ProcessRecordsTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask
}

@Singleton
@Secondary
class DefaultProcessRecordsTaskFactory(
    private val deserializer: Deserializer<DestinationMessage>,
) : ProcessRecordsTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask {
        return DefaultProcessRecordsTask(
            streamLoader,
            taskLauncher,
            fileEnvelope,
            deserializer,
        )
    }
}
