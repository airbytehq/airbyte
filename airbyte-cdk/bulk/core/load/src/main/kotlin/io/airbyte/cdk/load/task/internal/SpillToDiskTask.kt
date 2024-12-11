/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.collect.Range
import com.google.common.collect.TreeRangeSet
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.QueueReader
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.message.StreamCompleteEvent
import io.airbyte.cdk.load.message.StreamFlushEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.FlushStrategy
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.TimeWindowTrigger
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.InternalScope
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

interface SpillToDiskTask : InternalScope

/**
 * Reads records from the message queue and writes them to disk. This task is internal and is not
 * exposed to the implementor.
 *
 * TODO: Allow for the record batch size to be supplied per-stream. (Needed?)
 */
class DefaultSpillToDiskTask(
    private val spillFileProvider: SpillFileProvider,
    private val inputQueue: QueueReader<Reserved<DestinationStreamEvent>>,
    private val outputQueue: MultiProducerChannel<FileAggregateMessage>,
    private val flushStrategy: FlushStrategy,
    val streamDescriptor: DestinationStream.Descriptor,
    private val diskManager: ReservationManager,
    private val timeWindow: TimeWindowTrigger,
    private val taskLauncher: DestinationTaskLauncher
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val initialAccumulator = createNewAccumulator()

        val registration = outputQueue.registerProducer()
        registration.use {
            inputQueue.consume().fold(initialAccumulator) { acc, reserved ->
                reserved.use {
                    when (val event = it.value) {
                        is StreamRecordEvent -> accRecordEvent(acc, event)
                        is StreamCompleteEvent -> accStreamCompleteEvent(acc, event)
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
        val (spillFile, outputStream, range, sizeBytes) = acc
        // once we have received a record for the stream, consider the aggregate opened.
        timeWindow.open()

        // reserve enough room for the record
        diskManager.reserve(event.sizeBytes)

        // write to disk
        outputStream.write(event.record.serialized)
        outputStream.write("\n")

        // calculate whether we should flush
        val rangeProcessed = range.withNextAdjacentValue(event.index)
        val bytesProcessed = sizeBytes + event.sizeBytes
        val shouldPublish =
            flushStrategy.shouldFlush(streamDescriptor, rangeProcessed, bytesProcessed)

        if (!shouldPublish) {
            return FileAccumulator(spillFile, outputStream, rangeProcessed, bytesProcessed)
        }

        val file = SpilledRawMessagesLocalFile(spillFile, bytesProcessed, rangeProcessed)
        publishFile(file)
        outputStream.close()
        return createNewAccumulator()
    }

    /**
     * Handles accumulation of stream completion events, triggering a final flush if the aggregate
     * isn't empty.
     */
    private suspend fun accStreamCompleteEvent(
        acc: FileAccumulator,
        event: StreamCompleteEvent,
    ): FileAccumulator {
        val (spillFile, outputStream, range, sizeBytes) = acc
        if (sizeBytes == 0L) {
            log.info { "Skipping empty file $spillFile" }
            // Cleanup empty file
            spillFile.deleteExisting()
            // Directly send empty batch (skipping load step) to force bookkeeping; otherwise the
            // sync will hang forever. (Usually this happens because the entire stream was empty.)
            val empty =
                BatchEnvelope(
                    SimpleBatch(Batch.State.COMPLETE),
                    TreeRangeSet.create(),
                )
            taskLauncher.handleNewBatch(streamDescriptor, empty)
        } else {
            val nextRange = range.withNextAdjacentValue(event.index)
            val file =
                SpilledRawMessagesLocalFile(
                    spillFile,
                    sizeBytes,
                    nextRange,
                    endOfStream = true,
                )

            publishFile(file)
        }
        return FileAccumulator(
            spillFile,
            outputStream,
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
        val (spillFile, outputStream, range, sizeBytes) = acc
        val shouldPublish = timeWindow.isComplete()
        if (!shouldPublish) {
            return FileAccumulator(spillFile, outputStream, range, sizeBytes)
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
        return createNewAccumulator()
    }

    private fun createNewAccumulator(): FileAccumulator {
        return spillFileProvider.createTempFile().let { FileAccumulator(it, it.outputStream()) }
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
    private val spillFileProvider: SpillFileProvider,
    private val queueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>,
    private val flushStrategy: FlushStrategy,
    @Named("diskManager") private val diskManager: ReservationManager,
    private val clock: Clock,
    @Value("\${airbyte.flush.window-ms}") private val windowWidthMs: Long,
    @Named("fileAggregateQueue")
    private val fileAggregateQueue: MultiProducerChannel<FileAggregateMessage>,
) : SpillToDiskTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor
    ): SpillToDiskTask {
        val timeWindow = TimeWindowTrigger(clock, windowWidthMs)

        return DefaultSpillToDiskTask(
            spillFileProvider,
            queueSupplier.get(stream),
            fileAggregateQueue,
            flushStrategy,
            stream,
            diskManager,
            timeWindow,
            taskLauncher
        )
    }
}

data class FileAccumulator(
    val spillFile: Path,
    val spillFileOutputStream: OutputStream,
    val range: Range<Long>? = null,
    val sizeBytes: Long = 0,
)

data class SpilledRawMessagesLocalFile(
    val localFile: Path,
    val totalSizeBytes: Long,
    val indexRange: Range<Long>,
    val endOfStream: Boolean = false
)
