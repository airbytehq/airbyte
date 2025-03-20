package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.file.s3.S3Client
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.task.internal.ReservingDeserializingInputFlow
import io.airbyte.cdk.load.write.WriteOpOverride
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.File
import java.io.RandomAccessFile
import java.nio.file.Path
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import kotlin.time.measureTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.consumeAsFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class FileSegment(
    val fileUrl: String,
    val objectKey: String,
    val upload: StreamingUpload<S3Object>,
    val partNumber: Int,
    val partSize: Long,
    val callback: suspend () -> Unit = {}
)

@Singleton
class S3V2WriteOpOverride(
    private val client: S3Client,
    private val catalog: DestinationCatalog,
    private val config: S3V2Configuration<*>,
    private val pathFactory: PathFactory,
    private val reservingDeserializingInputFlow: ReservingDeserializingInputFlow,
    private val outputConsumer: Consumer<AirbyteMessage>,
    private val syncManager: SyncManager,
): WriteOpOverride {
    private val log = KotlinLogging.logger { }

    override val terminalCondition: TerminalCondition = SelfTerminating

    @OptIn(ExperimentalCoroutinesApi::class)
    override suspend fun execute() = coroutineScope {
        val mockPartQueue: Channel<FileSegment> = Channel(Channel.UNLIMITED)
        val streamCount = AtomicLong(catalog.streams.size.toLong())
        val totalBytesLoaded = AtomicLong(0L)
        val memoryManager = ReservationManager((Runtime.getRuntime().maxMemory() *
            config.maxMemoryRatioReservedForParts).toLong())
        try {
            withContext(Dispatchers.IO) {
                val duration = measureTime {
                    launch {
                        reservingDeserializingInputFlow.collect { (_, reservation) ->
                            when (val message = reservation.value) {
                                is GlobalCheckpoint -> {
                                    outputConsumer.accept(
                                        message.withDestinationStats(CheckpointMessage.Stats(0))
                                            .asProtocolMessage()
                                    )
                                }
                                is StreamCheckpoint -> {
                                    val (_, count) = syncManager.getStreamManager(message.checkpoint.stream)
                                    .markCheckpoint()
                                    log.info { "Flushing state" }
                                    outputConsumer.accept(
                                        message.withDestinationStats(
                                            CheckpointMessage.Stats(
                                                count
                                            )
                                        )
                                            .asProtocolMessage()
                                    )
                                    log.info { "Done flushing state" }
                                }
                                is DestinationFile -> {
                                    syncManager.getStreamManager(message.stream)
                                        .incrementReadCount()
                                    if (message.fileMessage.bytes == null) {
                                        throw IllegalStateException("This can't work unless you set FileMessage.bytes!")
                                    }
                                    val size = message.fileMessage.bytes!!
                                    log.info {
                                        "Reserving $size bytes for file ${message.fileMessage.fileUrl}"
                                    }
                                    memoryManager.reserve(size)
                                    log.info {
                                        "Successfully reserved $size bytes for file ${message.fileMessage.fileUrl}"
                                    }
                                    val numWholeParts = (size / config.partSizeBytes).toInt()
                                    val numParts =
                                        numWholeParts + if (size % config.partSizeBytes > 0) 1 else 0
                                    val lastPartSize = size % config.partSizeBytes
                                    val fileUrl = message.fileMessage.fileUrl!!
                                    log.info {
                                        "Breaking file $fileUrl (size=${size}B) into $numParts ${config.partSizeBytes}B parts"
                                    }
                                    val stream = catalog.getStream(message.stream)
                                    val directory = pathFactory.getFinalDirectory(stream)
                                    val sourceFileName = message.fileMessage.sourceFileUrl!!
                                    val objectKey = Path.of(directory, sourceFileName).toString()
                                    val upload = client.startStreamingUpload(objectKey)
                                    val partCounter = AtomicLong(numParts.toLong())
                                    repeat(numParts) { partNumber ->
                                        val partSize = if (partNumber == numParts - 1) lastPartSize else config.partSizeBytes
                                        mockPartQueue.send(
                                            FileSegment(
                                                fileUrl,
                                                objectKey,
                                                upload,
                                                partNumber + 1,
                                                if (partNumber == numParts - 1) lastPartSize else config.partSizeBytes
                                            ) {
                                                val partsRemaining = partCounter.decrementAndGet()
                                                log.info {
                                                    "Releasing $partSize bytes for part ${partNumber + 1} of file $fileUrl"
                                                }
                                                memoryManager.release(partSize)
                                                if (partsRemaining == 0L) {
                                                    log.info {
                                                        "Finished uploading $numParts parts of $fileUrl; deleting file and finishing upload"
                                                    }
                                                    File(fileUrl).delete()
                                                    log.info {
                                                        "Finished deleting"
                                                    }
                                                    upload.complete()
                                                    log.info {
                                                        "Finished completing the upload"
                                                    }
                                                } else {
                                                    log.info {
                                                        "Finished uploading part ${partNumber + 1} of $fileUrl. $partsRemaining parts remaining"
                                                    }
                                                }
                                            }
                                        )
                                    }
                                }

                                is DestinationFileStreamComplete,
                                is DestinationFileStreamIncomplete -> {
                                    if (streamCount.decrementAndGet() == 0L) {
                                        log.info {
                                            "Read final stream complete, closing mockPartQueue"
                                        }
                                        mockPartQueue.close()
                                    } else {
                                        log.info {
                                            "Read stream complete, ${streamCount.get()} streams remaining"
                                        }
                                    }
                                }

                                is DestinationRecordStreamComplete,
                                is DestinationRecordStreamIncomplete,
                                is DestinationRecord -> throw NotImplementedError("This hack is only for files")

                                Undefined ->
                                    log.warn {
                                        "Undefined message received. This should not happen."
                                    }
                            }
                            reservation.release()
                        }
                    }

                    (0 until config.numUploadWorkers).map {
                        async {
                            mockPartQueue.consumeAsFlow().collect { segment ->
                                log.info { "Starting upload to ${segment.objectKey} part ${segment.partNumber}" }
                                RandomAccessFile(segment.fileUrl, "r").use { file ->
                                    val partBytes = ByteArray(segment.partSize.toInt())
                                    file.seek((segment.partNumber - 1) * config.partSizeBytes)
                                    file.read(partBytes)
                                    segment.upload.uploadPart(partBytes, segment.partNumber)
                                    log.info {
                                        "Finished uploading part ${segment.partNumber} of ${segment.fileUrl}"
                                    }
                                    totalBytesLoaded.addAndGet(segment.partSize)
                                    segment.callback()
                                }
                            }
                        }
                    }.awaitAll()
                }
                log.info {
                    val mbs = totalBytesLoaded.get()
                        .toDouble() / 1024 / 1024 / duration.inWholeSeconds.toDouble()
                    "Uploaded ${totalBytesLoaded.get()} bytes in ${duration.inWholeSeconds}s (${mbs}MB/s)"
                }
            }
        } catch (e: Throwable) {
            log.error(e) { "Error uploading file, bailing" }
        }
    }
}
