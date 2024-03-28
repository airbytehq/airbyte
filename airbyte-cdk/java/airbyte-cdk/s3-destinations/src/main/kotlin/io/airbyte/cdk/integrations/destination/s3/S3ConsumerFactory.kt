/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.cdk.integrations.destination.record_buffer.BufferCreateFunction
import io.airbyte.cdk.integrations.destination.record_buffer.FlushBufferFunction
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.record_buffer.SerializedBufferingStrategy
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import java.util.function.Consumer
import java.util.function.Function
import java.util.stream.Collectors
import org.apache.commons.io.FileUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class S3ConsumerFactory {
    fun create(
        outputRecordCollector: Consumer<AirbyteMessage>,
        storageOperations: BlobStorageOperations,
        namingResolver: NamingConventionTransformer,
        onCreateBuffer: BufferCreateFunction,
        s3Config: S3DestinationConfig,
        catalog: ConfiguredAirbyteCatalog
    ): AirbyteMessageConsumer {
        val writeConfigs = createWriteConfigs(storageOperations, namingResolver, s3Config, catalog)
        return BufferedStreamConsumer(
            outputRecordCollector,
            onStartFunction(storageOperations, writeConfigs),
            SerializedBufferingStrategy(
                onCreateBuffer,
                catalog,
                flushBufferFunction(storageOperations, writeConfigs, catalog)
            ),
            onCloseFunction(storageOperations, writeConfigs),
            catalog
        ) { jsonNode: JsonNode? -> storageOperations.isValidData(jsonNode!!) }
    }

    private fun onStartFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>
    ): OnStartFunction {
        return OnStartFunction {
            LOGGER.info("Preparing bucket in destination started for {} streams", writeConfigs.size)
            for (writeConfig in writeConfigs) {
                if (writeConfig.syncMode == DestinationSyncMode.OVERWRITE) {
                    val namespace = writeConfig.namespace
                    val stream = writeConfig.streamName
                    val outputBucketPath = writeConfig.outputBucketPath
                    val pathFormat = writeConfig.pathFormat
                    LOGGER.info(
                        "Clearing storage area in destination started for namespace {} stream {} bucketObject {} pathFormat {}",
                        namespace,
                        stream,
                        outputBucketPath,
                        pathFormat
                    )
                    storageOperations.cleanUpBucketObject(
                        namespace!!,
                        stream,
                        outputBucketPath,
                        pathFormat
                    )
                    LOGGER.info(
                        "Clearing storage area in destination completed for namespace {} stream {} bucketObject {}",
                        namespace,
                        stream,
                        outputBucketPath
                    )
                }
            }
            LOGGER.info("Preparing storage area in destination completed.")
        }
    }

    private fun flushBufferFunction(
        storageOperations: BlobStorageOperations,
        writeConfigs: List<WriteConfig>,
        catalog: ConfiguredAirbyteCatalog?
    ): FlushBufferFunction {
        val pairToWriteConfig =
            writeConfigs
                .stream()
                .collect(
                    Collectors.toUnmodifiableMap(
                        Function { config: WriteConfig -> toNameNamespacePair(config) },
                        Function.identity()
                    )
                )

        return FlushBufferFunction {
            pair: AirbyteStreamNameNamespacePair,
            writer: SerializableBuffer ->
            LOGGER.info(
                "Flushing buffer for stream {} ({}) to storage",
                pair.name,
                FileUtils.byteCountToDisplaySize(writer.byteCount)
            )
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
                            writeConfig.namespace!!,
                            writeConfig.fullOutputPath
                        )!!
                    )
                }
            } catch (e: Exception) {
                LOGGER.error("Failed to flush and upload buffer to storage:", e)
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
                LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size)
                for (writeConfig in writeConfigs) {
                    storageOperations.cleanUpBucketObject(
                        writeConfig.fullOutputPath,
                        writeConfig.storedFiles
                    )
                    writeConfig.clearStoredFiles()
                }
                LOGGER.info("Cleaning up destination completed.")
            }
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(S3ConsumerFactory::class.java)
        private val SYNC_DATETIME: DateTime = DateTime.now(DateTimeZone.UTC)

        private fun createWriteConfigs(
            storageOperations: BlobStorageOperations,
            namingResolver: NamingConventionTransformer,
            config: S3DestinationConfig,
            catalog: ConfiguredAirbyteCatalog?
        ): List<WriteConfig> {
            return catalog!!
                .streams
                .stream()
                .map(toWriteConfig(storageOperations, namingResolver, config))
                .collect(Collectors.toList())
        }

        private fun toWriteConfig(
            storageOperations: BlobStorageOperations,
            namingResolver: NamingConventionTransformer,
            s3Config: S3DestinationConfig
        ): Function<ConfiguredAirbyteStream, WriteConfig> {
            return Function { stream: ConfiguredAirbyteStream ->
                Preconditions.checkNotNull(
                    stream.destinationSyncMode,
                    "Undefined destination sync mode"
                )
                val abStream = stream.stream
                val namespace = abStream.namespace
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
                LOGGER.info("Write config: {}", writeConfig)
                writeConfig
            }
        }

        private fun toNameNamespacePair(config: WriteConfig): AirbyteStreamNameNamespacePair {
            return AirbyteStreamNameNamespacePair(config.streamName, config.namespace)
        }
    }
}
