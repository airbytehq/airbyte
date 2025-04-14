package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.FileInputStream
import java.nio.file.Path

/**
 * Given an input stream of file references, reads the files and chunks them into parts, emitting
 * those parts to the outputQueue.
 */
class FilePartChunkTask<T>(
    val catalog: DestinationCatalog,
    val pathFactory: ObjectStoragePathFactory,
    val fileLoader: ObjectLoader,
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    val outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    val partition: Int
): Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = SelfTerminating

    private val partitioner = ObjectLoaderFormattedPartPartitioner<StreamKey, T>()

    override suspend fun execute() {
        inputQueue.consume(partition).collect { event ->
            when (event) {
                is PipelineMessage -> {
                    val stream = catalog.getStream(event.key.stream)
                    val file = event.value.fileReference!!

                    val key =
                        Path.of(
                            pathFactory.getFinalDirectory(stream),
                            file.stagingFileUrl,
                        ).toString()

                    val fileSize = file.fileSizeBytes
                    val localFileUrl = file.stagingFileUrl
                    // We expect a final marker even if size % partSize == 0.
                    val numParts = (fileSize / fileLoader.partSizeBytes).toInt() + 1

                    log.info { "Processing file $localFileUrl with $numParts parts" }
                    val localFile = File(localFileUrl)
                    val fileInputStream = localFile.inputStream()

                    val partFactory = FilePartFactory(
                        fileInputStream,
                        localFileUrl,
                        fileLoader.partSizeBytes.toInt(),
                        PartFactory(
                            key = key,
                            fileNumber = 0,
                        ),
                    )

                    do {
                        val outputPart = partFactory.getNextPart()
                        publishPart(event.key.stream, outputPart)
                    } while (!outputPart.isFinal)

                    log.info { "Finished reading $localFileUrl, deleting." }
                    fileInputStream.close()
                    localFile.delete()
                }

                is PipelineEndOfStream -> {
                    outputQueue.broadcast(PipelineEndOfStream(event.stream))
                }

                is PipelineHeartbeat<*, *> -> {
                    log.info { "Unexpected heartbeat msg. Ignoring..." }
                }
            }
        }
    }

    private suspend fun publishPart(
        stream: DestinationStream.Descriptor,
        part: Part,
    ) {
        val outputKey = ObjectKey(stream, part.key)
        val partition = partitioner.getPart(outputKey, 0, outputQueue.partitions)
        val outputMessage = PipelineMessage(emptyMap(), outputKey, part)
        outputQueue.publish(outputMessage, partition)
    }
}

class FilePartFactory(
    private val fileInputStream: FileInputStream,
    private val localFileUrl: String,
    private val partSizeBytes: Int,
    private val partFactory: PartFactory,
) {
    private val log = KotlinLogging.logger {}

    fun getNextPart(): Part {
        val bytes = fileInputStream.readNBytes(partSizeBytes)
        log.info { "Read ${bytes.size} bytes from $localFileUrl" }
        return if (bytes.isEmpty()) {
            partFactory.nextPart(null, isFinal = true)
        } else if (bytes.size < partSizeBytes) {
            partFactory.nextPart(bytes, isFinal = true)
        } else {
            partFactory.nextPart(bytes, isFinal = false)
        }
    }
}

