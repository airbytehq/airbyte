/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.message.StreamCompleteEvent
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.TimeWindowTrigger
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.InternalScope
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.util.takeUntilInclusive
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.load.util.withNextAdjacentValue
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.nio.file.Path
import java.time.Clock
import kotlin.io.path.outputStream
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
    private val spillFileProvider: SpillFileProvider,
    private val queue: QueueReader<Reserved<DestinationStreamEvent>>,
    private val flushStrategy: FlushStrategy,
    override val streamDescriptor: DestinationStream.Descriptor,
    private val launcher: DestinationTaskLauncher,
    private val diskManager: ReservationManager,
    private val timeWindow: TimeWindowTrigger,
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    data class ReadResult(
        val range: Range<Long>? = null,
        val sizeBytes: Long = 0,
        val hasReadEndOfStream: Boolean = false,
        val forceFlush: Boolean = false,
    )

    override suspend fun execute() {
        val tmpFile = spillFileProvider.createTempFile()
        val result =
            tmpFile.outputStream().use { outputStream ->
                queue
                    .consume()
                    .runningFold(ReadResult()) { (range, sizeBytes, _), reserved ->
                        reserved.use {
                            when (val wrapped = it.value) {
                                is StreamRecordEvent -> {
                                    // once we have received a record for the stream, consider the
                                    // aggregate opened.
                                    timeWindow.open()

                                    // reserve enough room for the record
                                    diskManager.reserve(wrapped.sizeBytes)
                                    // calculate whether we should flush
                                    val rangeProcessed = range.withNextAdjacentValue(wrapped.index)
                                    val bytesProcessed = sizeBytes + wrapped.sizeBytes
                                    val forceFlush =
                                        flushStrategy.shouldFlush(
                                            streamDescriptor,
                                            rangeProcessed,
                                            bytesProcessed
                                        )

                                    // write and return output
                                    outputStream.write(wrapped.record.serialized)
                                    outputStream.write("\n")
                                    ReadResult(
                                        rangeProcessed,
                                        bytesProcessed,
                                        forceFlush = forceFlush
                                    )
                                }
                                is StreamCompleteEvent -> {
                                    val nextRange = range.withNextAdjacentValue(wrapped.index)
                                    ReadResult(nextRange, sizeBytes, hasReadEndOfStream = true)
                                }
                                is StreamFlushEvent -> {
                                    val forceFlush = timeWindow.isComplete()
                                    if (forceFlush) {
                                        log.info {
                                            "Time window complete for $streamDescriptor@${timeWindow.openedAtMs} closing $tmpFile of (${sizeBytes}b)"
                                        }
                                    }
                                    ReadResult(range, sizeBytes, forceFlush = forceFlush)
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
        launcher.handleNewSpilledFile(streamDescriptor, file)
    }
}

interface SpillToDiskTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor
    ): SpillToDiskTask
}

@Singleton
class DefaultSpillToDiskTaskFactory(
    private val spillFileProvider: SpillFileProvider,
    private val queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
    private val flushStrategy: FlushStrategy,
    @Named("diskManager") private val diskManager: ReservationManager,
    private val clock: Clock,
    @Value("\${airbyte.flush.window-ms}") private val windowWidthMs: Long,
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor
    ): SpillToDiskTask {
        val timeWindow = TimeWindowTrigger(clock, windowWidthMs)

        return DefaultSpillToDiskTask(
            spillFileProvider,
            queueSupplier.get(stream),
            flushStrategy,
            stream,
            taskLauncher,
            diskManager,
            timeWindow,
        )
    }
}

data class SpilledRawMessagesLocalFile(
    val localFile: Path,
    val totalSizeBytes: Long,
    val indexRange: Range<Long>,
    val endOfStream: Boolean = false
)
