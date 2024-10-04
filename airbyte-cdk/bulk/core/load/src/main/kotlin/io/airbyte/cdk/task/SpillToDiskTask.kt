/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.file.TempFileProvider
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueReader
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.airbyte.cdk.state.FlushStrategy
import io.airbyte.cdk.util.takeUntilInclusive
import io.airbyte.cdk.util.withNextAdjacentValue
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.last
import kotlinx.coroutines.flow.runningFold
import kotlinx.coroutines.withContext

interface SpillToDiskTask : StreamTask

/**
 * Reads records from the message queue and writes them to disk. This task is internal and is not
 * exposed to the implementor.
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 */
class DefaultSpillToDiskTask(
    private val config: DestinationConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queueReader:
        MessageQueueReader<DestinationStream.Descriptor, DestinationRecordWrapped>,
    private val flushStrategy: FlushStrategy,
    override val stream: DestinationStream,
    private val launcher: DestinationTaskLauncher,
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    data class ReadResult(
        val range: Range<Long>? = null,
        val sizeBytes: Long = 0,
        val hasReadEndOfStream: Boolean = false,
        val forceFlush: Boolean = false,
    )

    override suspend fun execute() {
        val (path, result) =
            withContext(Dispatchers.IO) {
                val tmpFile =
                    tmpFileProvider.createTempFile(
                        config.tmpFileDirectory,
                        config.firstStageTmpFilePrefix,
                        config.firstStageTmpFileSuffix
                    )
                val result =
                    tmpFile.toFileWriter().use {
                        queueReader
                            .read(stream.descriptor)
                            .runningFold(ReadResult()) { (range, sizeBytes, _), wrapped ->
                                when (wrapped) {
                                    is StreamRecordWrapped -> {
                                        it.write(wrapped.record.serialized)
                                        it.write("\n")
                                        val nextRange = range.withNextAdjacentValue(wrapped.index)
                                        val nextSize = sizeBytes + wrapped.sizeBytes
                                        val forceFlush =
                                            flushStrategy.shouldFlush(stream, nextRange, nextSize)
                                        ReadResult(nextRange, nextSize, forceFlush = forceFlush)
                                    }
                                    is StreamCompleteWrapped -> {
                                        val nextRange = range.withNextAdjacentValue(wrapped.index)
                                        ReadResult(nextRange, sizeBytes, hasReadEndOfStream = true)
                                    }
                                }
                            }
                            .flowOn(Dispatchers.IO)
                            .takeUntilInclusive { it.hasReadEndOfStream || it.forceFlush }
                            .last()
                    }
                Pair(tmpFile, result)
            }

        /** Handle the result */
        val (range, sizeBytes, endOfStream) = result

        log.info { "Finished writing $range records (${sizeBytes}b) to $path" }

        // This could happen if the chunk only contained end-of-stream
        if (range == null) {
            // We read 0 records, do nothing
            return
        }

        val batch = SpilledRawMessagesLocalFile(path, sizeBytes)
        val wrapped = BatchEnvelope(batch, range)
        launcher.handleNewSpilledFile(stream, wrapped, endOfStream)
    }
}

interface SpillToDiskTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): SpillToDiskTask
}

@Singleton
class DefaultSpillToDiskTaskFactory(
    private val config: DestinationConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queueReader:
        MessageQueueReader<DestinationStream.Descriptor, DestinationRecordWrapped>,
    private val flushStrategy: FlushStrategy,
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): SpillToDiskTask {
        return DefaultSpillToDiskTask(
            config,
            tmpFileProvider,
            queueReader,
            flushStrategy,
            stream,
            taskLauncher,
        )
    }
}
