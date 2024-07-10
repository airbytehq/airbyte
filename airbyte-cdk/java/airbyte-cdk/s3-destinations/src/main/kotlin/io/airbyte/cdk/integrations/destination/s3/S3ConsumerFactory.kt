/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.FlushBufferFunction
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy
import io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory.Companion.getCreateFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer
import java.util.function.Function
import org.joda.time.DateTime
import org.joda.time.DateTimeZone

private val LOGGER = KotlinLogging.logger {}

class S3ConsumerFactory {
    private val DEFAULT_NAMESPACE = ""

    private fun onStartFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>
    ): OnStartFunction {
        return OnStartFunction {
            LOGGER.info {
                "Preparing bucket in destination started for ${writeConfigs.size} streams"
            }
            for (writeConfig in writeConfigs) {
                if (writeConfig.syncMode == DestinationSyncMode.OVERWRITE) {
                    val namespace = writeConfig.namespace
                    val stream = writeConfig.streamName
                    val outputBucketPath = writeConfig.outputBucketPath
                    val pathFormat = writeConfig.pathFormat
                    LOGGER.info {
                        "Clearing storage area in destination started for namespace $namespace " +
                            "stream $stream bucketObject $outputBucketPath pathFormat $pathFormat"
                    }
                    storageOperations.cleanUpBucketObject(
                        namespace,
                        stream,
                        outputBucketPath,
                        pathFormat
                    )
                    LOGGER.info {
                        "Clearing storage area in destination completed for namespace $namespace stream $stream bucketObject $outputBucketPath"
                    }
                }
            }
            LOGGER.info { "Preparing storage area in destination completed." }
        }
    }

    private fun flushBufferFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>,
        catalog: ConfiguredAirbyteCatalog?,
        defaultNamespace: String
    ): FlushBufferFunction {
        val pairToWriteConfig =
            writeConfigs.associateBy { toNameNamespacePair(it, defaultNamespace) }

        return FlushBufferFunction {
            pair: AirbyteStreamNameNamespacePair,
            writer: SerializableBuffer ->
            LOGGER.info {
                "Flushing buffer for stream ${pair.name} ({FileUtils.byteCountToDisplaySize(writer.byteCount)}) to storage"
            }
            require(pairToWriteConfig.containsKey(pair)) {
                String.format(
                    "Message contained record from a stream %s that was not in the catalog. \ncatalog: %s",
                    pair,
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
                            writeConfig.fullOutputPath
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
        return OnCloseFunction { hasFailed: Boolean, _: Map<StreamDescriptor, StreamSyncSummary> ->
            if (hasFailed) {
                LOGGER.info { "Cleaning up destination started for ${writeConfigs.size} streams" }
                for (writeConfig in writeConfigs) {
                    storageOperations.cleanUpBucketObject(
                        writeConfig.fullOutputPath,
                        writeConfig.storedFiles
                    )
                    writeConfig.clearStoredFiles()
                }
                LOGGER.info { "Cleaning up destination completed." }
            }
        }
    }

    fun createAsync(
        outputRecordCollector: Consumer<AirbyteMessage>,
        storageOps: S3StorageOperations,
        s3Config: S3DestinationConfig,
        catalog: ConfiguredAirbyteCatalog
    ): SerializedAirbyteMessageConsumer? {
        val writeConfigs = createWriteConfigs(storageOps, s3Config, catalog)
        val createFunction =
            getCreateFunction(
                s3Config,
                Function<String, BufferStorage> { fileExtension: String ->
                    FileBuffer(fileExtension)
                },
                DEFAULT_NAMESPACE
            )
        return AsyncStreamConsumer(
            outputRecordCollector,
            onStartFunction(storageOps, writeConfigs),
            onCloseFunction(storageOps, writeConfigs),
            S3DestinationFlushFunction(
                optimalBatchSizeBytes = FileBuffer.MAX_PER_STREAM_BUFFER_SIZE_BYTES,
                {
                    SerializedBufferingStrategy(
                        createFunction,
                        catalog,
                        flushBufferFunction(storageOps, writeConfigs, catalog, DEFAULT_NAMESPACE)
                    )
                },
                DEFAULT_NAMESPACE
            ),
            catalog,
            BufferManager(DEFAULT_NAMESPACE)
        )
    }

    companion object {

        private val SYNC_DATETIME: DateTime = DateTime.now(DateTimeZone.UTC)

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
                        syncMode
                    )
                LOGGER.info { "Write config: $writeConfig" }
                writeConfig
            }
        }

        private fun toNameNamespacePair(
            config: WriteConfig,
            defaultNamespace: String
        ): AirbyteStreamNameNamespacePair {
            return AirbyteStreamNameNamespacePair(
                config.streamName,
                config.namespace ?: defaultNamespace
            )
        }
    }
}
