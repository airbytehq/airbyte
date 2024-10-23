/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.LocalFile
import io.airbyte.cdk.load.file.TempFileProvider
import io.airbyte.cdk.load.message.DestinationRecordWrapped
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.message.StreamCompleteWrapped
import io.airbyte.cdk.load.message.StreamRecordWrapped
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.InternalScope
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.util.takeUntilInclusive
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.load.util.withNextAdjacentValue
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.last
import kotlinx.coroutines.flow.runningFold

interface SpillToDiskTask : StreamLevel, InternalScope

/**
 * Reads records from the message queue and writes them to disk. This task is internal and is not
 * exposed to the implementor.
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 */
class DefaultSpillToDiskTask(
    private val config: DestinationConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queue: QueueReader<Reserved<DestinationRecordWrapped>>,
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
        val tmpFile =
            tmpFileProvider.createTempFile(
                config.tmpFileDirectory,
                config.firstStageTmpFilePrefix,
                config.firstStageTmpFileSuffix
            )
        val result =
            tmpFile.toFileWriter().use { writer ->
                queue
                    .consume()
                    .runningFold(ReadResult()) { (range, sizeBytes, _), reserved ->
                        reserved.use {
                            when (val wrapped = it.value) {
                                is StreamRecordWrapped -> {
                                    writer.write(wrapped.record.serialized)
                                    writer.write("\n")
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
                    }
                    .takeUntilInclusive { it.hasReadEndOfStream || it.forceFlush }
                    .last()
            }

        /** Handle the result */
        val (range, sizeBytes, endOfStream) = result

        log.info { "Finished writing $range records (${sizeBytes}b) to $tmpFile" }

        // This could happen if the chunk only contained end-of-stream
        if (range == null) {
            // We read 0 records, do nothing
            return
        }

        val file = SpilledRawMessagesLocalFile(tmpFile, sizeBytes, range, endOfStream)
        launcher.handleNewSpilledFile(stream, file)
    }
}

interface SpillToDiskTaskFactory {
    fun make(taskLauncher: DestinationTaskLauncher, stream: DestinationStream): SpillToDiskTask
}

@Singleton
class DefaultSpillToDiskTaskFactory(
    private val config: DestinationConfiguration,
    private val tmpFileProvider: TempFileProvider,
    private val queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>,
    private val flushStrategy: FlushStrategy,
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream
    ): SpillToDiskTask {
        return DefaultSpillToDiskTask(
            config,
            tmpFileProvider,
            queueSupplier.get(stream.descriptor),
            flushStrategy,
            stream,
            taskLauncher,
        )
    }
}

data class SpilledRawMessagesLocalFile(
    val localFile: LocalFile,
    val totalSizeBytes: Long,
    val indexRange: Range<Long>,
    val endOfStream: Boolean = false
)
