package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.FileLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Path
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.yield


class FileLoaderProcessFileTask(
    val catalog: DestinationCatalog,
    val pathFactory: ObjectStoragePathFactory,
    val fileLoader: FileLoader,
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationFile>>,
    val batchQueue: QueueWriter<BatchUpdate>,
    val outputQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    val partition: Int
): Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = SelfTerminating

    private val partitioner = ObjectLoaderPartPartitioner<DestinationFile>()

    // Since we're denormalizing the parts, we need to force bookkeeping to work properly.
    inner class PartCallback(
        private val stream: DestinationStream.Descriptor,
        numParts: Int,
        private val checkpointCounts: Map<CheckpointId, Long>,
    ) {
        private val numParts = AtomicLong(numParts.toLong())

        suspend fun onUpload() {
            if (numParts.decrementAndGet() == 0L) {
                batchQueue.publish(BatchStateUpdate(stream, checkpointCounts, Batch.State.COMPLETE))
            }
        }
    }

    override suspend fun execute() {
        inputQueue.consume(partition).collect { event ->
            when (event) {
                is PipelineMessage -> {
                    val stream = catalog.getStream(event.key.stream)
                    val file = event.value
                    val key =
                        Path.of(pathFactory.getFinalDirectory(stream), "${file.fileMessage.fileRelativePath}")
                            .toString()
                    val fileSize = file.fileMessage.bytes!!
                    val fileName = file.fileMessage.fileUrl!!
                    // We expect a final marker even if size % partSize == 0.
                    val numParts = (fileSize / fileLoader.partSizeBytes).toInt() + 1

                    val partFactory =
                        PartFactory(
                            key = key,
                            fileNumber = 0,
                        )

                    log.info { "Processing file $fileName with $numParts parts" }
                    val localFile = File(fileName)
                    val fileInputStream = localFile.inputStream()
                    val callback = PartCallback(event.key.stream, numParts, event.checkpointCounts)

                    while (true) {
                        val bytes = fileInputStream.readNBytes(fileLoader.partSizeBytes.toInt())
                        log.info { "Read ${bytes.size} bytes from $fileName" }

                        if (bytes.isEmpty()) {
                            val outputPart = partFactory.nextPart(null, isFinal = true)
                            publishPart(callback, event.key.stream, outputPart)
                            break
                        } else if (bytes.size < fileLoader.partSizeBytes) {
                            val outputPart = partFactory.nextPart(bytes, isFinal = true)
                            publishPart(callback, event.key.stream, outputPart)
                            break
                        } else {
                            val outputPart = partFactory.nextPart(bytes, isFinal = false)
                            publishPart(callback, event.key.stream, outputPart)
                        }
                    }
                    log.info { "Finished reading $fileName, deleting." }
                    fileInputStream.close()
                    localFile.delete()
                }

                is PipelineEndOfStream -> {
                    outputQueue.broadcast(PipelineEndOfStream(event.stream))
                }
            }
        }
    }

    private suspend fun publishPart(callback: PartCallback, stream: DestinationStream.Descriptor, part: Part) {
        val outputKey = ObjectKey(stream, part.key)
        val partition = partitioner.getPart(outputKey, fileLoader.numPartWorkers)
        val outputMessage = PipelineMessage(emptyMap(), outputKey, part) {
            callback.onUpload()
        }
        outputQueue.publish(outputMessage, partition)
    }
}
