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
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
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
    private val partSizeBytes: Long,
    private val fileSizeBytes: Long,
    private val stream: DestinationStream,
    private val fileNumber: AtomicLong,
    private val fileNameMapper: suspend (String) -> String
) : BatchAccumulator {
    private val log = KotlinLogging.logger {}

    // Hack because AtomicReference doesn't support lazily evaluated blocks.
    private val key = "key"
    private val currentObject = ConcurrentHashMap<String, ObjectInProgress<U>>()

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        // Start a new object if there is not one in progress.
        val partialUpload =
            currentObject.getOrPut(key) {
                val fileNo = fileNumber.incrementAndGet()
                ObjectInProgress(
                    partFactory =
                        PartFactory(
                            key =
                                fileNameMapper(
                                    pathFactory.getPathToFile(
                                        stream,
                                        fileNo,
                                    )
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
        val bufferSize = partialUpload.writer.bufferSize
        val newSize = partialUpload.partFactory.totalSize + bufferSize
        if (newSize >= fileSizeBytes || endOfStream) {

            // If we have reached target file size, clear the object and yield a final part.
            val bytes = partialUpload.writer.finish()
            partialUpload.writer.close()
            val part = partialUpload.partFactory.nextPart(bytes, isFinal = true)

            log.info {
                val reason = if (endOfStream) "end of stream" else "file size ${fileSizeBytes}b"
                "${partialUpload.partFactory.key}: buffer ${bufferSize}b; total: ${newSize}b; $reason reached, yielding final part ${part.partIndex} (size=${bytes?.size}b)"
            }

            currentObject.remove(key)
            return LoadablePart(part)
        } else if (bufferSize >= partSizeBytes) {
            // If we have not reached file size, but have reached part size, yield a non-final part.
            val bytes = partialUpload.writer.takeBytes()
            val part = partialUpload.partFactory.nextPart(bytes)
            log.info {
                "${partialUpload.partFactory.key}: buffer ${bufferSize}b; total ${newSize}b; part size ${partSizeBytes}b reached, yielding part ${part.partIndex}"
            }

            return LoadablePart(part)
        } else {
            // If we have not reached either the file or part size, yield a null part.
            // TODO: Change this to a generator interface so we never have to do this.
            val part = partialUpload.partFactory.nextPart(null)
            log.info {
                "${partialUpload.partFactory.key}: buffer ${bufferSize}b; total ${newSize}b; part size ${partSizeBytes}b not reached, yielding null part ${part.partIndex}"
            }

            return LoadablePart(part)
        }
    }
}
