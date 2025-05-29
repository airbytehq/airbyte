/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.WriteConfiguration
import io.airbyte.cdk.file.TempFileProvider
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueReader
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.runningFold
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.withContext
import kotlinx.coroutines.yield

interface SpillToDiskTask : Task

/**
 * Reads records from the message queue and writes them to disk. This task is internal and is not
 * exposed to the implementor.
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 */
class DefaultSpillToDiskTask(
    private val config: WriteConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queueReader: MessageQueueReader<DestinationStream, DestinationRecordWrapped>,
    private val stream: DestinationStream,
    private val launcher: DestinationTaskLauncher
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    data class ReadResult(
        val range: Range<Long>? = null,
        val sizeBytes: Long = 0,
        val hasReadEndOfStream: Boolean = false,
    )

    // Necessary because Guava's Range/sets have no "empty" range
    private fun withIndex(range: Range<Long>?, index: Long): Range<Long> {
        return if (range == null) {
            Range.singleton(index)
        } else if (index != range.upperEndpoint() + 1) {
            throw IllegalStateException("Expected index ${range.upperEndpoint() + 1}, got $index")
        } else {
            range.span(Range.singleton(index))
        }
    }

    override suspend fun execute() {
        do {
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
                                .readChunk(stream, config.recordBatchSizeBytes)
                                .runningFold(ReadResult()) { (range, sizeBytes, _), wrapped ->
                                    when (wrapped) {
                                        is StreamRecordWrapped -> {
                                            val nextRange = withIndex(range, wrapped.index)
                                            it.write(wrapped.record.serialized)
                                            it.write("\n")
                                            ReadResult(nextRange, sizeBytes + wrapped.sizeBytes)
                                        }
                                        is StreamCompleteWrapped -> {
                                            val nextRange = withIndex(range, wrapped.index)
                                            return@runningFold ReadResult(
                                                nextRange,
                                                sizeBytes,
                                                true
                                            )
                                        }
                                    }
                                }
                                .flowOn(Dispatchers.IO)
                                .toList()
                        }
                    Pair(tmpFile, result.last())
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
            launcher.handleNewSpilledFile(stream, wrapped)

            yield()
        } while (!endOfStream)
    }
}

interface SpillToDiskTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): SpillToDiskTask
}

@Singleton
class DefaultSpillToDiskTaskFactory(
    private val config: WriteConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queueReader: MessageQueueReader<DestinationStream, DestinationRecordWrapped>
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): SpillToDiskTask {
        return DefaultSpillToDiskTask(config, tmpFileProvider, queueReader, stream, taskLauncher)
    }
}
