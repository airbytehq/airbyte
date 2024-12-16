package io.airbyte.cdk.load.write.object_storage

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.object_storage.LoadablePart
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.BatchAccumulator
import java.io.File
import java.nio.file.Path

class FilePartAccumulator(
    private val pathFactory: ObjectStoragePathFactory,
    private val stream: DestinationStream,
    private val taskLauncher: DestinationTaskLauncher,
    private val outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
): BatchAccumulator {
    override suspend fun processFilePart(file: DestinationFile, index: Long) {
        val key =
            Path.of(pathFactory.getFinalDirectory(stream), "${file.fileMessage.fileRelativePath}")
                .toString()

        val part = PartFactory(
            key = key,
            fileNumber = index,
        )

        val localFile = File(file.fileMessage.fileUrl)
        val fileInputStream = localFile.inputStream()

        while (true) {
            val bytePart = ByteArray(1024 * 1024 * 10)
            val read = fileInputStream.read(bytePart)

            if (read == -1) {
                val filePart: ByteArray? = null
                val batch = LoadablePart(part.nextPart(filePart, isFinal = true))
                handleFilePart(batch, stream.descriptor, index)
                break
            } else if (read < bytePart.size) {
                val filePart: ByteArray = bytePart.copyOfRange(0, read)
                val batch = LoadablePart(part.nextPart(filePart, isFinal = true))
                handleFilePart(batch, stream.descriptor, index)
                break
            } else {
                val batch = LoadablePart(part.nextPart(bytePart, isFinal = false))
                handleFilePart(batch, stream.descriptor, index)
            }
        }
        localFile.delete()
    }

    private suspend fun handleFilePart(batch: Batch,
                                       streamDescriptor: DestinationStream.Descriptor,
                                       index: Long,) {

        val wrapped = BatchEnvelope(batch, Range.singleton(index), streamDescriptor)
        outputQueue.publish(wrapped)

    }
}
