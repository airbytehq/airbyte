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
import io.airbyte.cdk.load.message.LimitedMessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
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
import io.airbyte.cdk.load.task.StreamLevel
import io.airbyte.cdk.load.task.implementor.FileQueueMessage
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
import kotlin.io.path.outputStream
import kotlinx.coroutines.flow.fold

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
    private val diskManager: ReservationManager,
    private val timeWindow: TimeWindowTrigger,
    private val spillFileQueue: LimitedMessageQueue<FileQueueMessage>,
    private val taskLauncher: DestinationTaskLauncher
) : SpillToDiskTask {
    private val log = KotlinLogging.logger {}

    data class ReadResult(
        val spillFile: Path,
        val spillFileOutputStream: OutputStream,
        val range: Range<Long>? = null,
        val sizeBytes: Long = 0,
    )

    override suspend fun execute() {
        val initialResult =
            spillFileProvider.createTempFile().let { ReadResult(it, it.outputStream()) }
        spillFileQueue.take().use {
            queue.consume().fold(initialResult) {
                (spillFile, outputStream, range, sizeBytes),
                reserved ->
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

                            outputStream.write(wrapped.record.serialized)
                            outputStream.write("\n")

                            if (forceFlush) {
                                val file =
                                    SpilledRawMessagesLocalFile(
                                        spillFile,
                                        bytesProcessed,
                                        rangeProcessed
                                    )
                                publishFile(file)
                                val nextTmpFile = spillFileProvider.createTempFile()
                                outputStream.close()
                                ReadResult(nextTmpFile, nextTmpFile.outputStream())
                            } else {
                                ReadResult(spillFile, outputStream, rangeProcessed, bytesProcessed)
                            }
                        }
                        is StreamCompleteEvent -> {
                            val nextRange = range.withNextAdjacentValue(wrapped.index)
                            val file =
                                SpilledRawMessagesLocalFile(
                                    spillFile,
                                    sizeBytes,
                                    nextRange,
                                    endOfStream = true
                                )
                            publishFile(file)
                            ReadResult(
                                spillFile,
                                outputStream,
                                range,
                                sizeBytes
                            ) // this will be the last message
                        }
                        is StreamFlushEvent -> {
                            val forceFlush = timeWindow.isComplete()
                            if (forceFlush) {
                                log.info {
                                    "Time window complete for $streamDescriptor@${timeWindow.openedAtMs} closing $spillFile of (${sizeBytes}b)"
                                }
                            }

                            if (range != null && sizeBytes > 0L) {
                                val file =
                                    SpilledRawMessagesLocalFile(
                                        spillFile,
                                        sizeBytes,
                                        range,
                                        endOfStream = false
                                    )
                                publishFile(file)
                                val nextTmpFile = spillFileProvider.createTempFile()
                                outputStream.close()
                                ReadResult(nextTmpFile, nextTmpFile.outputStream())
                            } else {
                                ReadResult(spillFile, outputStream, range, sizeBytes)
                            }
                        }
                    }
                }
            }
        }
    }

    private suspend fun publishFile(file: SpilledRawMessagesLocalFile) {
        if (file.totalSizeBytes == 0L) {
            log.info { "Skipping empty file $file" }
            // Annoying hack to force bookkeeping even in the event that all we
            // processed was end-of-stream; otherwise the sync will hang forever.
            // (Usually this happens because the entire stream was empty.)
            val dummy = BatchEnvelope(SimpleBatch(Batch.State.COMPLETE), TreeRangeSet.create())
            taskLauncher.handleNewBatch(streamDescriptor, dummy)
            return
        }
        log.info { "Publishing file $file" }
        spillFileQueue.publish(FileQueueMessage(streamDescriptor, file))
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
    @Named("spillFileQueue") private val spillFileQueue: LimitedMessageQueue<FileQueueMessage>,
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
            diskManager,
            timeWindow,
            spillFileQueue,
            taskLauncher
        )
    }
}

data class SpilledRawMessagesLocalFile(
    val localFile: Path,
    val totalSizeBytes: Long,
    val indexRange: Range<Long>,
    val endOfStream: Boolean = false
)
