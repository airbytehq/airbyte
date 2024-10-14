/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.DestinationStreamComplete
import io.airbyte.cdk.load.message.DestinationStreamIncomplete
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorTask
import io.airbyte.cdk.load.task.StreamTask
import io.airbyte.cdk.load.write.DestinationWriterInternal
import io.airbyte.cdk.load.write.StreamLoader
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
class DefaultProcessRecordsTask<B>(
    override val stream: DestinationStream,
    private val destinationWriter: DestinationWriterInternal<B>,
    private val taskLauncher: DestinationTaskLauncher<B>,
    private val fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    private val deserializer: Deserializer<DestinationMessage>,
) : ProcessRecordsTask {
    override suspend fun execute() {
        val log = KotlinLogging.logger {}

        log.info { "Fetching stream loader for ${stream.descriptor}" }
        val streamLoader = destinationWriter.getOrCreateStreamLoader(stream)

        log.info { "Processing records from ${fileEnvelope.batch.payload.localFile}" }
        val nextBatch =
            try {
                fileEnvelope.batch.payload.localFile.toFileReader().use { reader ->
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
                    streamLoader.processRecords(records, fileEnvelope.batch.payload.totalSizeBytes)
                }
            } finally {
                log.info { "Processing completed, deleting ${fileEnvelope.batch.payload.localFile}" }
                fileEnvelope.batch.payload.localFile.delete()
            }

        val wrapped = fileEnvelope.withBatch(nextBatch)
        taskLauncher.handleNewBatch(stream, wrapped)
    }
}

interface ProcessRecordsTaskFactory<B> {
    fun make(
        taskLauncher: DestinationTaskLauncher<B>,
        stream: DestinationStream,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask
}

@Singleton
@Secondary
class DefaultProcessRecordsTaskFactory<B>(
    private val deserializer: Deserializer<DestinationMessage>,
    private val destinationWriter: DestinationWriterInternal<B>,
) : ProcessRecordsTaskFactory<B> {
    override fun make(
        taskLauncher: DestinationTaskLauncher<B>,
        stream: DestinationStream,
        fileEnvelope: BatchEnvelope<SpilledRawMessagesLocalFile>,
    ): ProcessRecordsTask {
        return DefaultProcessRecordsTask(
            stream,
            destinationWriter,
            taskLauncher,
            fileEnvelope,
            deserializer,
        )
    }
}
