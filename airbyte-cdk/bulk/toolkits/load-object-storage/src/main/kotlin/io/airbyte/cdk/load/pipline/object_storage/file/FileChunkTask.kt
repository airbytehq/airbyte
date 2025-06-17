/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path

/**
 * Given an input stream of file references, reads the files and chunks them into parts, emitting
 * those parts to the partQueue. Once finished chunking a file, it deletes it from local storage.
 */
class FileChunkTask<T>(
    loader: ObjectLoader,
    private val catalog: DestinationCatalog,
    private val pathFactory: ObjectStoragePathFactory,
    private val fileHandleFactory: FileHandleFactory,
    private val uploadIdGenerator: UploadIdGenerator,
    private val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val partitioner: ObjectLoaderFormattedPartPartitioner<StreamKey, T>,
    private val partition: Int,
) : Task {
    private val log = KotlinLogging.logger {}

    private val partSizeBytes = loader.partSizeBytes.toInt()

    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() = inputQueue.consume(partition).collect(this::handleEvent)

    @VisibleForTesting
    suspend fun handleEvent(event: PipelineEvent<StreamKey, DestinationRecordRaw>) {
        when (event) {
            is PipelineEndOfStream -> {
                partQueue.broadcast(PipelineEndOfStream(event.stream))
            }
            is PipelineHeartbeat<*, *> -> {
                log.info { "Unexpected heartbeat. Ignoring..." }
            }
            is PipelineMessage -> {
                val file = event.value.fileReference!!
                val stream = catalog.getStream(event.key.stream)

                val filePath =
                    Path.of(
                            pathFactory.getFinalDirectory(stream),
                            file.sourceFileRelativePath,
                        )
                        .toString()

                // We enrich the record with the file_path. Ideally the schema modification
                // should be handled outside of this scope but the hook doesn't exist.
                event.context?.parentRecord?.enrichRecordWithFilePath(filePath)

                val localFile = fileHandleFactory.make(file.stagingFileUrl)
                val fileInputStream = localFile.inputStream()

                // iterate over the file and emit a part for each partSizeBytes read
                val parts =
                    FilePartIterator(
                        fileInputStream,
                        partSizeBytes,
                        filePath,
                    )

                val fileSize = file.fileSizeBytes
                // Why +1? We expect a final marker even if size % partSize == 0.
                val numParts = (fileSize / partSizeBytes) + 1
                log.info { "Processing file ${file.stagingFileUrl} with $numParts parts" }

                val uploadId = uploadIdGenerator.generate()
                val objectKey = ObjectKey(stream.descriptor, filePath, uploadId)

                parts.forEach {
                    log.info { "Read ${it.bytes?.size ?: 0} bytes from ${file.stagingFileUrl}" }

                    publishPart(objectKey, it, event.context!!)
                }

                fileInputStream.close()
                localFile.delete()
            }
        }
    }

    private suspend fun publishPart(
        outputKey: ObjectKey,
        part: Part,
        pipelineContext: PipelineContext,
    ) {
        val partition = partitioner.getPart(outputKey, partition, partQueue.partitions)

        val formattedPart = ObjectLoaderPartFormatter.FormattedPart(part)

        val outputMessage =
            PipelineMessage(emptyMap(), outputKey, formattedPart, context = pipelineContext)

        partQueue.publish(outputMessage, partition)
    }

    companion object {
        const val COLUMN_NAME_AIRBYTE_FILE_PATH = "_airbyte_file_path"

        fun DestinationRecordRaw.enrichRecordWithFilePath(filePath: String) {
            (stream.schema as? ObjectType)
                ?.properties
                ?.put(COLUMN_NAME_AIRBYTE_FILE_PATH, FieldType(StringType, nullable = true))
            asJsonRecord().let { jsonNode ->
                (jsonNode as ObjectNode).put(COLUMN_NAME_AIRBYTE_FILE_PATH, filePath)
            }
        }
    }
}
