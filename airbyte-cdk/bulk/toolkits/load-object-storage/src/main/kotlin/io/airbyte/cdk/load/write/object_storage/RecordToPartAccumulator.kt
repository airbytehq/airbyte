/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.object_storage.*
import io.airbyte.cdk.load.write.BatchAccumulator
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.OutputStream
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

data class ObjectInProgress<T : OutputStream>(
    val partFactory: PartFactory,
    val writer: BufferedFormattingWriter<T>,
)

class RecordToPartAccumulator<U : OutputStream>(
    private val pathFactory: ObjectStoragePathFactory,
    private val bufferedWriterFactory: BufferedFormattingWriterFactory<U>,
    private val recordBatchSizeBytes: Long,
    private val stream: DestinationStream,
    private val fileNumber: AtomicLong,
) : BatchAccumulator {
    private val log = KotlinLogging.logger {}

    // Hack because AtomicReference doesn't support lazily evaluated blocks.
    private val key = "key"
    private val currentObject = ConcurrentHashMap<String, ObjectInProgress<U>>()

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        // Start a new object if there is not one in progress.
        val partialUpload =
            currentObject.getOrPut(key) {
                val fileNo = fileNumber.getAndIncrement()
                ObjectInProgress(
                    partFactory =
                        PartFactory(
                            key =
                                pathFactory.getPathToFile(
                                    stream,
                                    fileNo,
                                    isStaging = pathFactory.supportsStaging
                                ),
                            fileNumber = fileNo
                        ),
                    writer = bufferedWriterFactory.create(stream),
                )
            }

        // Add all the records to the formatting writer.
        log.info { "Accumulating ${totalSizeBytes}b records for ${partialUpload.partFactory.key}" }
        records.forEach { partialUpload.writer.accept(it) }
        partialUpload.writer.flush()

        // Check if we have reached the target size.
        val newSize = partialUpload.partFactory.totalSize + partialUpload.writer.bufferSize
        if (newSize >= recordBatchSizeBytes || endOfStream) {

            // If we have reached target size, clear the object and yield a final part.
            val bytes = partialUpload.writer.finish()
            partialUpload.writer.close()
            val part = partialUpload.partFactory.nextPart(bytes, isFinal = true)

            log.info {
                "Size $newSize/${recordBatchSizeBytes}b reached (endOfStream=$endOfStream), yielding final part ${part.partIndex} (empty=${part.isEmpty})"
            }

            currentObject.remove(key)
            return LoadablePart(part)
        } else {
            // If we have not reached target size, just yield the next part.
            val bytes = partialUpload.writer.takeBytes()
            val part = partialUpload.partFactory.nextPart(bytes)
            log.info {
                "Size $newSize/${recordBatchSizeBytes}b not reached, yielding part ${part.partIndex} (empty=${part.isEmpty})"
            }

            return LoadablePart(part)
        }
    }
}
