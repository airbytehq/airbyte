/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.message.Batch
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.message.DestinationRecord
import io.airbyte.cdk.message.DestinationRecordMessage
import io.airbyte.cdk.message.DestinationStreamComplete
import io.airbyte.cdk.message.SpooledRawMessagesLocalFile
import io.airbyte.cdk.state.StreamManager
import io.airbyte.cdk.state.StreamsManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlin.io.path.bufferedReader
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Wraps @[StreamLoader.processRecords] and feeds it a lazy iterator over the last batch of spooled
 * records. On completion it rewraps the processed batch in the old envelope and kicks off batch
 * handling and/or close stream tasks.
 *
 * TODO: The batch handling logic here is identical to that in @[ProcessBatchTask]. Both should be
 * moved to the task launcher.
 */
class ProcessRecordsTask(
    private val streamLoader: StreamLoader,
    private val streamManager: StreamManager,
    private val taskLauncher: DestinationTaskLauncher,
    private val fileEnvelope: BatchEnvelope<SpooledRawMessagesLocalFile>,
    private val deserializer: Deserializer<DestinationMessage>,
) : Task {
    override suspend fun execute() {
        val nextBatch =
            withContext(Dispatchers.IO) {
                val records =
                    fileEnvelope.batch.localPath
                        .bufferedReader(Charsets.UTF_8)
                        .lineSequence()
                        .map {
                            when (val record = deserializer.deserialize(it)) {
                                is DestinationRecordMessage -> record
                                else ->
                                    throw IllegalStateException(
                                        "Expected record message, got ${record::class}"
                                    )
                            }
                        }
                        .takeWhile { it !is DestinationStreamComplete }
                        .map { it as DestinationRecord }
                        .iterator()
                streamLoader.processRecords(records, fileEnvelope.batch.totalSizeBytes)
            }

        val wrapped = fileEnvelope.withBatch(nextBatch)
        streamManager.updateBatchState(wrapped)

        // TODO: Move this logic into the task launcher
        if (nextBatch.state != Batch.State.COMPLETE) {
            taskLauncher.startProcessBatchTask(streamLoader, wrapped)
        } else if (streamManager.isBatchProcessingComplete()) {
            taskLauncher.startCloseStreamTasks(streamLoader)
        }
    }
}

@Singleton
@Secondary
class ProcessRecordsTaskFactory(
    private val streamsManager: StreamsManager,
    private val deserializer: Deserializer<DestinationMessage>,
) {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
        fileEnvelope: BatchEnvelope<SpooledRawMessagesLocalFile>,
    ): ProcessRecordsTask {
        return ProcessRecordsTask(
            streamLoader,
            streamsManager.getManager(streamLoader.stream),
            taskLauncher,
            fileEnvelope,
            deserializer,
        )
    }
}
