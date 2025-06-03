/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Path

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "state is guaranteed to be non-null by Kotlin's type system"
)
class FilePartAccumulatorLegacy(
    private val pathFactory: ObjectStoragePathFactory,
    private val stream: DestinationStream,
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val loadStrategy: ObjectLoader
) {
    val log = KotlinLogging.logger {}
    val partitioner =
        ObjectLoaderFormattedPartPartitioner<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>()

    suspend fun handleFileMessage(file: DestinationFile, index: Long, checkpointId: CheckpointId) {
        val key =
            Path.of(pathFactory.getFinalDirectory(stream), "${file.fileMessage.fileRelativePath}")
                .toString()

        val partFactory =
            PartFactory(
                key = key,
                fileNumber = index,
            )

        val localFile = File(file.fileMessage.fileUrl)
        val fileInputStream = localFile.inputStream()

        while (true) {
            val bytePart =
                ByteArray(ObjectStorageUploadConfiguration.DEFAULT_PART_SIZE_BYTES.toInt())
            val read = fileInputStream.read(bytePart)
            log.info { "Read $read bytes from file" }

            if (read == -1) {
                val filePart: ByteArray? = null
                val part = partFactory.nextPart(filePart, isFinal = true)
                handleFilePart(part, stream.descriptor, checkpointId)
                break
            } else if (read < bytePart.size) {
                val filePart: ByteArray = bytePart.copyOfRange(0, read)
                val part = partFactory.nextPart(filePart, isFinal = true)
                handleFilePart(part, stream.descriptor, checkpointId)
                break
            } else {
                val part = partFactory.nextPart(bytePart, isFinal = false)
                handleFilePart(part, stream.descriptor, checkpointId)
            }
        }
        fileInputStream.close()
        localFile.delete()
    }

    private suspend fun handleFilePart(
        part: Part,
        streamDescriptor: DestinationStream.Descriptor,
        checkpointId: CheckpointId,
    ) {
        val objectKey = ObjectKey(streamDescriptor, part.key)
        val countMap =
            if (part.isFinal) {
                mapOf(checkpointId to CheckpointValue(1, 1))
            } else {
                emptyMap()
            }
        val newPipelineShimMessage =
            PipelineMessage(countMap, objectKey, ObjectLoaderPartFormatter.FormattedPart(part))

        val outputPartition = partitioner.getPart(objectKey, 0, loadStrategy.numUploadWorkers)
        outputQueue.publish(newPipelineShimMessage, outputPartition)
    }
}

class FilePartAccumulatorFactory(
    private val pathFactory: ObjectStoragePathFactory,
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val loadStrategy: ObjectLoader
) {
    fun make(
        stream: DestinationStream,
    ): FilePartAccumulatorLegacy =
        FilePartAccumulatorLegacy(pathFactory, stream, outputQueue, loadStrategy)
}
