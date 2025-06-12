/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.FlushBufferFunction
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy
import io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory.Companion.getCreateFunction
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.text.DecimalFormat
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Stream
import org.apache.commons.io.FileUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone

private val LOGGER = KotlinLogging.logger {}

class S3ConsumerFactory {
    fun create(
        outputRecordCollector: Consumer<AirbyteMessage>,
        storageOperations: BlobStorageOperations,
        onCreateBuffer: BufferCreateFunction,
        s3Config: S3DestinationConfig,
        catalog: ConfiguredAirbyteCatalog
    ): AirbyteMessageConsumer {
        val writeConfigs = createWriteConfigs(storageOperations, s3Config, catalog)
        return BufferedStreamConsumer(
            outputRecordCollector,
            onStartFunction(storageOperations, writeConfigs),
            SerializedBufferingStrategy(
                onCreateBuffer,
                catalog,
                flushBufferFunction(storageOperations, writeConfigs, catalog)
            ),
            onCloseFunction(storageOperations, writeConfigs),
            catalog,
            { jsonNode: JsonNode? -> storageOperations.isValidData(jsonNode!!) },
            null,
        )
    }

    private fun onStartFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>
    ): OnStartFunction {
        return OnStartFunction {
            LOGGER.info {
                "Preparing bucket in destination started for ${writeConfigs.size} streams"
            }
            for (writeConfig in writeConfigs) {
                val namespace = writeConfig.namespace
                val stream = writeConfig.streamName
                val outputBucketPath = writeConfig.outputBucketPath
                val pathFormat = writeConfig.pathFormat
                if (!isAppendSync(writeConfig)) {
                    LOGGER.info {
                        "Listing objects to cleanup for namespace $namespace " +
                            "stream $stream bucketObject $outputBucketPath pathFormat $pathFormat"
                    }
                    writeConfig.objectsFromOldGeneration.addAll(
                        keysForOverwriteDeletion(
                            writeConfig,
                            storageOperations,
                        ),
                    )
                    LOGGER.info {
                        "Marked ${writeConfig.objectsFromOldGeneration.size} keys for deletion at end of sync " +
                            "for namespace $namespace stream $stream bucketObject $outputBucketPath"
                    }
                } else {
                    LOGGER.info {
                        "Skipping clearing of storage area in destination for namespace $namespace " +
                            "stream $stream bucketObject $outputBucketPath pathFormat $pathFormat"
                    }
                }
            }
            LOGGER.info { "Preparing storage area in destination completed." }
        }
    }

    private fun flushBufferFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>,
        catalog: ConfiguredAirbyteCatalog
    ): FlushBufferFunction {
        val pairToWriteConfig = writeConfigs.associateBy { toNameNamespacePair(it) }

        return FlushBufferFunction {
            pair: AirbyteStreamNameNamespacePair,
            writer: SerializableBuffer ->
            LOGGER.info {
                "Flushing buffer for stream ${pair.name} ({FileUtils.byteCountToDisplaySize(writer.byteCount)}) to storage"
            }
            require(pairToWriteConfig.containsKey(pair)) {
                String.format(
                    "Message contained record from a stream [namespace=\"%s\", name=\"%s\"] that was not in the catalog. \ncatalog: %s",
                    pair.namespace,
                    pair.name,
                    Jsons.serialize(catalog)
                )
            }

            val writeConfig = pairToWriteConfig[pair]
            try {
                writer.use {
                    writer.flush()
                    writeConfig!!.addStoredFile(
                        storageOperations.uploadRecordsToBucket(
                            writer,
                            writeConfig.namespace,
                            writeConfig.fullOutputPath,
                            writeConfig.generationId
                        )!!
                    )
                }
            } catch (e: Exception) {
                LOGGER.error(e) { "Failed to flush and upload buffer to storage:" }
                throw RuntimeException("Failed to upload buffer to storage", e)
            }
        }
    }

    private fun onCloseFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>
    ): OnCloseFunction {

        val streamDescriptorToWriteConfig =
            writeConfigs.associateBy {
                StreamDescriptor().withNamespace(it.namespace).withName(it.streamName)
            }
        return OnCloseFunction {
            _: Boolean,
            streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary> ->
            // On stream success clean up the objects marked for deletion per stream. This is done
            // on per-stream basis
            streamSyncSummaries.forEach { (streamDescriptor, streamSummary) ->
                val streamSuccessful =
                    streamSummary.terminalStatus ==
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                if (streamSuccessful) {
                    val writeConfig = streamDescriptorToWriteConfig[streamDescriptor]!!
                    if (writeConfig.objectsFromOldGeneration.isNotEmpty()) {
                        // Although S3API is safe to send empty list of keys, just avoiding
                        // unnecessary S3 call
                        // Logic to determine what to delete is in onStart so not doing any
                        // redundant checks for
                        // destinationSyncMode.
                        LOGGER.info {
                            "Found ${writeConfig.objectsFromOldGeneration.size} marked for deletion in namespace: ${streamDescriptor.namespace},stream: ${streamDescriptor.name} " +
                                "Proceeding with cleaning up the objects"
                        }
                        storageOperations.cleanUpObjects(writeConfig.objectsFromOldGeneration)
                        LOGGER.info {
                            "Cleaning up completed for namespace: ${streamDescriptor.namespace},stream: ${streamDescriptor.name}"
                        }
                    }
                } else {
                    LOGGER.info {
                        "Stream not successful with status ${streamSummary.terminalStatus} for namespace: ${streamDescriptor.namespace}, name: ${streamDescriptor.name} " +
                            "Skipping deletion of any old objects marked for deletion."
                    }
                }
            }
        }
    }

    fun createAsync(
        outputRecordCollector: Consumer<AirbyteMessage>,
        storageOps: S3StorageOperations,
        s3Config: S3DestinationConfig,
        catalog: ConfiguredAirbyteCatalog,
        memoryRatio: Double,
        nThreads: Int,
        featureFlags: FeatureFlags
    ): SerializedAirbyteMessageConsumer {
        val writeConfigs = createWriteConfigs(storageOps, s3Config, catalog)
        // Buffer creation function: yields a file buffer that converts
        // incoming data to the correct format for the destination.

        val generationAndSyncIds =
            catalog.streams.associate { stream ->
                val descriptor =
                    StreamDescriptor()
                        .withNamespace(stream.stream.namespace)
                        .withName(stream.stream.name)
                descriptor to Pair(stream.generationId, stream.syncId)
            }

        // Parquet has significantly higher overhead. This small adjustment
        // results in a ~5x performance improvement.
        val adjustedMemoryRatio =
            if (s3Config.formatConfig!!.format == FileUploadFormat.PARQUET) {
                memoryRatio * 0.6 // ie 0.5 => 0.3
            } else {
                memoryRatio
            }

        // This needs to be called before the creation of the flush function because it updates
        // writeConfigs!
        val onStartFunction = onStartFunction(storageOps, writeConfigs)

        val streamDescriptorToWriteConfig =
            writeConfigs.associateBy {
                StreamDescriptor().withNamespace(it.namespace).withName(it.streamName)
            }
        val flushFunction =
            if (featureFlags.useFileTransfer()) {
                FileTransferDestinationFlushFunction(
                    streamDescriptorToWriteConfig,
                    storageOps,
                    featureFlags
                )
            } else {
                val createFunction =
                    getCreateFunction(
                        s3Config,
                        Function<String, BufferStorage> { fileExtension: String ->
                            FileBuffer(fileExtension)
                        },
                        useV2FieldNames = true
                    )
                S3DestinationFlushFunction(
                    // Ensure the file buffer is always larger than the memory buffer,
                    // as the file buffer will be flushed at the end of the memory flush.
                    optimalBatchSizeBytes =
                        (FileBuffer.MAX_PER_STREAM_BUFFER_SIZE_BYTES * 0.9).toLong(),
                    {
                        // Yield a new BufferingStrategy every time we flush (for thread-safety).
                        SerializedBufferingStrategy(
                            createFunction,
                            catalog,
                            flushBufferFunction(storageOps, writeConfigs, catalog)
                        )
                    },
                    generationAndSyncIds
                )
            }

        return AsyncStreamConsumer(
            outputRecordCollector,
            onStartFunction,
            onCloseFunction(storageOps, writeConfigs),
            flushFunction,
            catalog,
            // S3 has no concept of default namespace
            // In the "namespace from destination case", the namespace
            // is simply omitted from the path.
            BufferManager(
                defaultNamespace = null,
                maxMemory = (Runtime.getRuntime().maxMemory() * adjustedMemoryRatio).toLong()
            ),
            workerPool = Executors.newFixedThreadPool(nThreads),
            flushOnEveryMessage = featureFlags.useFileTransfer()
        )
    }

    private class FileTransferDestinationFlushFunction(
        val streamDescriptorToWriteConfig: Map<StreamDescriptor, WriteConfig>,
        val storageOps: S3StorageOperations,
        val featureFlags: FeatureFlags
    ) : DestinationFlushFunction {
        override fun flush(
            streamDescriptor: StreamDescriptor,
            stream: Stream<PartialAirbyteMessage>
        ) {
            val records = stream.toList()
            val writeConfig = streamDescriptorToWriteConfig.getValue(streamDescriptor)
            if (records.isEmpty()) {
                return
            }
            if (records.size > 1) {
                throw RuntimeException(
                    "the destinationFlushFunction for RAW_FILES should be called with only 1 record"
                )
            }
            val file = records[0].record!!.file
            if (file == null) {
                throw RuntimeException(MISSING_FILE_FIELD_IN_FILE_TRANSFER_ERROR_MESSAGE)
            }
            val absolutePath = file.fileUrl!!
            val relativePath = file.fileRelativePath!!
            val fullObjectKey = writeConfig.fullOutputPath + relativePath
            val dataFile = File(absolutePath)
            val fileSize = dataFile.length()
            val startTimeMs = System.currentTimeMillis()
            storageOps.loadDataIntoBucket(
                fullObjectKey = fullObjectKey,
                fileName = dataFile.name,
                fileContent = dataFile.inputStream(),
                generationId = writeConfig.generationId
            )
            val elapsedTimeSeconds = (System.currentTimeMillis() - startTimeMs) / 1_000.0
            val speedMBps = (fileSize / (1_024 * 1_024)) / elapsedTimeSeconds
            LOGGER.info {
                "wrote ${FileUtils.byteCountToDisplaySize(fileSize)} file in $elapsedTimeSeconds s, for a speed of ${decimalFormat.format(speedMBps)} MBps"
            }
            dataFile.delete()
        }

        override val optimalBatchSizeBytes: Long = 1L
    }

    private fun isAppendSync(writeConfig: WriteConfig): Boolean {
        // This is an additional safety check, that this really is OVERWRITE
        // mode, this avoids bad things happening like deleting all objects
        // in APPEND mode.
        return writeConfig.minimumGenerationId == 0L &&
            writeConfig.syncMode != DestinationSyncMode.OVERWRITE
    }

    private fun keysForOverwriteDeletion(
        writeConfig: WriteConfig,
        storageOperations: BlobStorageOperations
    ): List<String> {
        // Guards to fail fast
        if (writeConfig.minimumGenerationId == 0L) {
            throw IllegalArgumentException(
                "Keys should not be marked for deletion when not in OVERWRITE mode"
            )
        }
        if (writeConfig.minimumGenerationId != writeConfig.generationId) {
            throw IllegalArgumentException("Hybrid refreshes are not yet supported.")
        }

        // This is truncate sync and try to determine if the current generation
        // data is already present
        val namespace = writeConfig.namespace
        val stream = writeConfig.streamName
        val outputBucketPath = writeConfig.outputBucketPath
        val pathFormat = writeConfig.pathFormat
        // generationId is missing, assume the last sync was ran in non-resumeable refresh
        // mode,
        // cleanup files
        val currentGenerationId =
            storageOperations.getStageGeneration(namespace, stream, outputBucketPath, pathFormat)
        var filterByCurrentGen = false
        if (currentGenerationId != null) {
            // if minGen = gen = retrievedGen and skip clean up
            val hasDataFromCurrentGeneration = currentGenerationId == writeConfig.generationId
            if (hasDataFromCurrentGeneration) {
                LOGGER.info {
                    "Preserving data from previous sync for stream ${writeConfig.streamName} since it matches the current generation ${writeConfig.generationId}"
                }
                // There could be data dangling from T-2 sync if current generation failed in T-1
                // sync.
                filterByCurrentGen = true
            } else {
                LOGGER.info {
                    "No data exists from previous sync for stream ${writeConfig.streamName} from current generation ${writeConfig.generationId}, " +
                        "proceeding to clean up existing data"
                }
            }
        } else {
            LOGGER.info {
                "Missing generationId from the lastModified object, proceeding with cleanup for stream ${writeConfig.streamName}"
            }
        }

        return storageOperations.listExistingObjects(
            namespace,
            stream,
            outputBucketPath,
            pathFormat,
            currentGenerationId =
                if (filterByCurrentGen) {
                    writeConfig.generationId
                } else {
                    null
                },
        )
    }

    companion object {
        val decimalFormat = DecimalFormat("#.###")
        private val SYNC_DATETIME: DateTime = DateTime.now(DateTimeZone.UTC)
        val MISSING_FILE_FIELD_IN_FILE_TRANSFER_ERROR_MESSAGE =
            "the RECORD message doesn't have a file field in file transfer mode"

        private fun createWriteConfigs(
            storageOperations: BlobStorageOperations,
            config: S3DestinationConfig,
            catalog: ConfiguredAirbyteCatalog?
        ): List<WriteConfig> {
            return catalog!!.streams.map { toWriteConfig(storageOperations, config).apply(it) }
        }

        private fun toWriteConfig(
            storageOperations: BlobStorageOperations,
            s3Config: S3DestinationConfig
        ): Function<ConfiguredAirbyteStream, WriteConfig> {
            return Function { stream: ConfiguredAirbyteStream ->
                Preconditions.checkNotNull(
                    stream.destinationSyncMode,
                    "Undefined destination sync mode"
                )
                if (stream.generationId == null || stream.minimumGenerationId == null) {
                    throw ConfigErrorException(
                        "You must upgrade your platform version to use this connector version. Either downgrade your connector or upgrade platform to 0.63.7"
                    )
                }
                val abStream = stream.stream
                val namespace: String? = abStream.namespace
                val streamName = abStream.name
                val bucketPath = s3Config.bucketPath
                val customOutputFormat = java.lang.String.join("/", bucketPath, s3Config.pathFormat)
                val fullOutputPath =
                    storageOperations.getBucketObjectPath(
                        namespace,
                        streamName,
                        SYNC_DATETIME,
                        customOutputFormat
                    )
                val syncMode = stream.destinationSyncMode
                val writeConfig =
                    WriteConfig(
                        namespace,
                        streamName,
                        bucketPath!!,
                        customOutputFormat,
                        fullOutputPath!!,
                        syncMode,
                        stream.generationId,
                        stream.minimumGenerationId
                    )
                LOGGER.info { "Write config: $writeConfig" }
                writeConfig
            }
        }

        private fun toNameNamespacePair(config: WriteConfig): AirbyteStreamNameNamespacePair {
            return AirbyteStreamNameNamespacePair(config.streamName, config.namespace)
        }
    }
}
