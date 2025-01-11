/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.message.StreamEndEvent
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.TimeWindowTrigger
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.KillableScope
import io.airbyte.cdk.load.task.implementor.FileAggregateMessage
import io.airbyte.cdk.load.util.use
import io.airbyte.cdk.load.util.withNextAdjacentValue
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.OutputStream
import java.nio.file.Path
import java.time.Clock
import kotlin.io.path.deleteExisting
import kotlin.io.path.outputStream
import kotlinx.coroutines.flow.fold

interface SpillToDiskTask : KillableScope

/**
 * Reads records from the message queue and writes them to disk. Completes once the upstream
 * inputQueue is closed.
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 */
class DefaultSpillToDiskTask(
    private val fileAccFactory: FileAccumulatorFactory,
    private val inputQueue: QueueReader<Reserved<DestinationStreamEvent>>,
    private val outputQueue: MultiProducerChannel<FileAggregateMessage>,
    private val flushStrategy: FlushStrategy,
    val streamDescriptor: DestinationStream.Descriptor,
    private val diskManager: ReservationManager,
    private val taskLauncher: DestinationTaskLauncher,
    private val processEmptyFiles: Boolean,
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val initialAccumulator = fileAccFactory.make()

        outputQueue.use {
            inputQueue.consume().fold(initialAccumulator) { acc, reserved ->
                reserved.use {
                    when (val event = it.value) {
                        is StreamRecordEvent -> accRecordEvent(acc, event)
                        is StreamEndEvent -> accStreamEndEvent(acc, event)
                        is StreamFlushEvent -> accFlushEvent(acc)
                    }
                }
            }
        }
    }

    /**
     * Handles accumulation of record events, triggering a publish downstream when the flush
     * strategy returns true—generally when a size (MB) thresholds has been reached.
     */
    private suspend fun accRecordEvent(
        acc: FileAccumulator,
        event: StreamRecordEvent,
    ): FileAccumulator {
        val (spillFile, outputStream, timeWindow, range, sizeBytes) = acc
        // once we have received a record for the stream, consider the aggregate opened.
        timeWindow.open()

        // reserve enough room for the record
        diskManager.reserve(event.sizeBytes)

        // write to disk
        outputStream.write(event.payload.serialized)
        outputStream.write("\n")

        // calculate whether we should flush
        val rangeProcessed = range.withNextAdjacentValue(event.index)
        val bytesProcessed = sizeBytes + event.sizeBytes
        val shouldPublish =
            flushStrategy.shouldFlush(streamDescriptor, rangeProcessed, bytesProcessed)

        if (!shouldPublish) {
            return FileAccumulator(
                spillFile,
                outputStream,
                timeWindow,
                rangeProcessed,
                bytesProcessed,
            )
        }

        val file = SpilledRawMessagesLocalFile(spillFile, bytesProcessed, rangeProcessed)
        publishFile(file)
        outputStream.close()
        return fileAccFactory.make()
    }

    /**
     * Handles accumulation of stream end events (complete or incomplete), triggering a final flush
     * if the aggregate isn't empty.
     */
    private suspend fun accStreamEndEvent(
        acc: FileAccumulator,
        event: StreamEndEvent,
    ): FileAccumulator {
        val (spillFile, outputStream, timeWindow, range, sizeBytes) = acc
        if (sizeBytes == 0L && !processEmptyFiles) {
            log.info { "Skipping empty file $spillFile" }
            // Cleanup empty file
            spillFile.deleteExisting()
            // Directly send empty batch (skipping load step) to force bookkeeping; otherwise the
            // sync will hang forever. (Usually this happens because the entire stream was empty.)
            val empty =
                BatchEnvelope(
                    SimpleBatch(Batch.State.COMPLETE),
                    TreeRangeSet.create(),
                    streamDescriptor
                )
            taskLauncher.handleNewBatch(streamDescriptor, empty)
        } else {
            val nextRange =
                if (sizeBytes == 0L) {
                    null
                } else {
                    range.withNextAdjacentValue(event.index)
                }
            val file =
                SpilledRawMessagesLocalFile(
                    spillFile,
                    sizeBytes,
                    nextRange,
                    endOfStream = true,
                )

            publishFile(file)
        }
        // this result should not be used as upstream will close the channel.
        return FileAccumulator(
            spillFile,
            outputStream,
            timeWindow,
            range,
            sizeBytes,
        )
    }

    /**
     * Handles accumulation of flush tick events, triggering publish when the window has been open
     * for longer than the cutoff (default: 15 minutes)
     */
    private suspend fun accFlushEvent(
        acc: FileAccumulator,
    ): FileAccumulator {
        val (spillFile, outputStream, timeWindow, range, sizeBytes) = acc
        val shouldPublish = timeWindow.isComplete()
        if (!shouldPublish) {
            return FileAccumulator(spillFile, outputStream, timeWindow, range, sizeBytes)
        }

        log.info {
            "Time window complete for $streamDescriptor@${timeWindow.openedAtMs} closing $spillFile of (${sizeBytes}b)"
        }

        val file =
            SpilledRawMessagesLocalFile(
                spillFile,
                sizeBytes,
                range!!,
                endOfStream = false,
            )
        publishFile(file)
        outputStream.close()
        return fileAccFactory.make()
    }

    private suspend fun publishFile(file: SpilledRawMessagesLocalFile) {
        log.info { "Publishing file aggregate: $file for processing..." }
        outputQueue.publish(FileAggregateMessage(streamDescriptor, file))
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
    private val config: DestinationConfiguration,
    private val fileAccFactory: FileAccumulatorFactory,
    private val queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
    private val flushStrategy: FlushStrategy,
    @Named("diskManager") private val diskManager: ReservationManager,
    @Named("fileAggregateQueue")
    private val fileAggregateQueue: MultiProducerChannel<FileAggregateMessage>,
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor
    ): SpillToDiskTask {

        return DefaultSpillToDiskTask(
            fileAccFactory,
            queueSupplier.get(stream),
            fileAggregateQueue,
            flushStrategy,
            stream,
            diskManager,
            taskLauncher,
            config.processEmptyFiles,
        )
    }
}

@Singleton
class FileAccumulatorFactory(
    @Value("\${airbyte.flush.window-ms}") private val windowWidthMs: Long,
    private val spillFileProvider: SpillFileProvider,
    private val clock: Clock,
) {
    fun make(): FileAccumulator {
        val file = spillFileProvider.createTempFile()
        return FileAccumulator(
            file,
            file.outputStream(),
            TimeWindowTrigger(clock, windowWidthMs),
        )
    }
}

data class FileAccumulator(
    val spillFile: Path,
    val spillFileOutputStream: OutputStream,
    val timeWindow: TimeWindowTrigger,
    val range: Range<Long>? = null,
    val sizeBytes: Long = 0,
)

data class SpilledRawMessagesLocalFile(
    val localFile: Path,
    val totalSizeBytes: Long,
    val indexRange: Range<Long>?,
    val endOfStream: Boolean = false
) {
    val isEmpty
        get() = totalSizeBytes == 0L
}
