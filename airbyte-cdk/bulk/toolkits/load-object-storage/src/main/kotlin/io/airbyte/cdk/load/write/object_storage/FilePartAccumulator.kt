/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import com.google.common.collect.Range
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.object_storage.LoadablePart
import io.airbyte.cdk.load.write.FileBatchAccumulator
import java.io.File
import java.lang.IllegalStateException
import java.nio.file.Path

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "state is guaranteed to be non-null by Kotlin's type system"
)
class FilePartAccumulator(
    private val pathFactory: ObjectStoragePathFactory,
    private val stream: DestinationStream,
    private val outputQueue: MultiProducerChannel<BatchEnvelope<*>>,
) : FileBatchAccumulator {
    override suspend fun processFilePart(file: DestinationFile, index: Long) {
        val key =
            Path.of(pathFactory.getFinalDirectory(stream), "${file.fileMessage.fileRelativePath}")
                .toString()

        val part =
            PartFactory(
                key = key,
                fileNumber = index,
            )

        val localFile = File(file.fileMessage.fileUrl)
        val fileInputStream = localFile.inputStream()

        while (true) {
            val bytePart =
                ByteArray(ObjectStorageUploadConfiguration.DEFAULT_FILE_SIZE_BYTES.toInt())
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
        val canWriteToLocalFile = localFile.canWrite()
        val canReadLocalFile = localFile.canRead()
        val canExecuteLocalFile = localFile.canExecute()
        val canWriteToParent = localFile.parentFile.canWrite()
        val canReadParent = localFile.parentFile.canRead()
        val canWExecuteParent = localFile.parentFile.canExecute()
        val result = localFile.delete()
//        throw IllegalStateException("File: $localFile — " +
//            "didDelete = $result " +
//            "canWriteToLocalFile = $canWriteToLocalFile" +
//            "canReadLocalFile = $canReadLocalFile" +
//            "canExecuteLocalFile = $canExecuteLocalFile" +
//            "canWriteToParent = $canWriteToParent" +
//            "canReadParent = $canReadParent" +
//            "canWExecuteParent = $canWExecuteParent")
    }

    private suspend fun handleFilePart(
        batch: Batch,
        streamDescriptor: DestinationStream.Descriptor,
        index: Long,
    ) {
        val wrapped = BatchEnvelope(batch, Range.singleton(index), streamDescriptor)
        outputQueue.publish(wrapped)
    }
}
