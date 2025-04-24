/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.factory.object_storage.ObjectKey
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.FileInputStream
import java.nio.file.Path
import java.util.UUID

/**
 * Given an input stream of file references, reads the files and chunks them into parts, emitting
 * those parts to the partQueue.
 */
class FileChunkTask<T>(
    val catalog: DestinationCatalog,
    val pathFactory: ObjectStoragePathFactory,
    val fileLoader: ObjectLoader,
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    val partQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    val partition: Int
) : Task {
    companion object {
        const val COLUMN_NAME_AIRBYTE_FILE_PATH = "_airbyte_file_path"

        fun DestinationRecordRaw.enrichRecordWithFilePath(filePath: String) {
            (stream.schema as? ObjectType)
                ?.properties
                ?.put(
                    COLUMN_NAME_AIRBYTE_FILE_PATH,
                    FieldType(StringType, nullable = true)
                )
            asRawJson().let { jsonNode ->
                (jsonNode as ObjectNode).put(COLUMN_NAME_AIRBYTE_FILE_PATH, filePath)
            }
        }
    }

    private val log = KotlinLogging.logger {}

    override val terminalCondition: TerminalCondition = OnEndOfSync

    private val partitioner = ObjectLoaderFormattedPartPartitioner<StreamKey, T>()

    override suspend fun execute() {
        inputQueue.consume(partition).collect { event ->
            when (event) {
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

                    val fileSize = file.fileSizeBytes
                    val localFileUrl = file.stagingFileUrl
                    // We expect a final marker even if size % partSize == 0.
                    val numParts = (fileSize / fileLoader.partSizeBytes).toInt() + 1

                    log.info { "Processing file $localFileUrl with $numParts parts" }
                    val localFile = File(localFileUrl)
                    val fileInputStream = localFile.inputStream()

                    val partFactory =
                        FilePartFactory(
                            fileInputStream,
                            localFileUrl,
                            fileLoader.partSizeBytes.toInt(),
                            PartFactory(
                                key = filePath,
                                fileNumber = 0,
                            ),
                        )

                    // generate a unique upload id to keep track of the upload in the case of file
                    // name collisions
                    val uploadId = UUID.randomUUID().toString()
                    val objectKey = ObjectKey(stream.descriptor, filePath, uploadId)

                    do {
                        val outputPart = partFactory.getNextPart()
                        publishPart(objectKey, outputPart, event.context!!)
                    } while (!outputPart.isFinal)

                    log.info { "Finished reading $localFileUrl, deleting." }
                    fileInputStream.close()
                    localFile.delete()
                }
                is PipelineEndOfStream -> {
                    partQueue.broadcast(PipelineEndOfStream(event.stream))
                }
                is PipelineHeartbeat<*, *> -> {
                    log.info { "Unexpected heartbeat. Ignoring..." }
                }
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
