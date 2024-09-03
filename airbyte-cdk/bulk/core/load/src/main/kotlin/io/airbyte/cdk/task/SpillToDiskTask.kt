/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import com.google.common.collect.Range
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.WriteConfiguration
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.DestinationRecordWrapped
import io.airbyte.cdk.message.MessageQueueReader
import io.airbyte.cdk.message.SpooledRawMessagesLocalFile
import io.airbyte.cdk.message.StreamCompleteWrapped
import io.airbyte.cdk.message.StreamRecordWrapped
import io.airbyte.cdk.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.nio.file.Files
import kotlin.io.path.bufferedWriter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.runningFold
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.withContext
import kotlinx.coroutines.yield

/**
 * Reads records from the message queue and writes them to disk. This task is internal and does not
 * interact with the task launcher.
 *
 * TODO: Use an injected interface for creating the filewriter (for testing, custom overrides).
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 *
 * TODO: Migrate the batch processing logic to the task launcher. Also, this batch should also be
 * recorded, as it will allow the stream manager to report exactly how many records have been
 * spilled.
 */
class SpillToDiskTask(
    private val config: WriteConfiguration,
    private val queueReader: MessageQueueReader<DestinationStream, DestinationRecordWrapped>,
    private val streamLoader: StreamLoader,
    private val launcher: DestinationTaskLauncher
) : Task {
    private val log = KotlinLogging.logger {}

    data class ReadResult(
        val range: Range<Long>? = null,
        val sizeBytes: Long = 0,
        val hasReadEndOfStream: Boolean = false,
    )

    // Necessary because Guava's has no "empty" range
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
                    /** Create a temporary file to write the records to */
                    val path = Files.createTempFile(config.firstStageTmpFilePrefix, ".jsonl")
                    val result =
                        path.bufferedWriter(Charsets.UTF_8).use {
                            queueReader
                                .readChunk(streamLoader.stream, config.recordBatchSizeBytes)
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
                    Pair(path, result.last())
                }

            /** Handle the result */
            val (range, sizeBytes, endOfStream) = result

            log.info { "Finished writing $range records (${sizeBytes}b) to $path" }

            // This could happen if the chunk only contained end-of-stream
            if (range == null) {
                // We read 0 records, do nothing
                return
            }

            val wrapped = BatchEnvelope(SpooledRawMessagesLocalFile(path, sizeBytes), range)
            launcher.startProcessRecordsTask(streamLoader, wrapped)

            yield()
        } while (!endOfStream)
    }
}

@Singleton
class SpillToDiskTaskFactory(
    private val config: WriteConfiguration,
    private val queueReader: MessageQueueReader<DestinationStream, DestinationRecordWrapped>
) {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        streamLoader: StreamLoader,
    ): SpillToDiskTask {
        return SpillToDiskTask(config, queueReader, streamLoader, taskLauncher)
    }
}
