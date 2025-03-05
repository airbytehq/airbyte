/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.SocketTestConfig
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.azureBlobStorage.GENERATION_ID_METADATA_KEY_OVERRIDE
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

class AzureBlobStorageConfiguration<T : OutputStream>(
    // Client-facing configuration
    override val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,
    override val estimatedRecordMemoryOverheadRatio: Double = 5.0,
    override val processEmptyFiles: Boolean = true,

    // TODO remove these from config and hardcode them in AzureBlobStorageObjectLoader
    //   after we finish performance tuning
    val numPartWorkers: Int = 2,
    val numUploadWorkers: Int = 5,
    val maxMemoryRatioReservedForParts: Double = 0.4,
    val objectSizeBytes: Long = 200L * 1024 * 1024,
    val partSizeBytes: Long = 10L * 1024 * 1024,

    // Temporary for socket
    override val numSockets: Int,
    override val inputSerializationFormat: InputSerializationFormat,
    override val inputBufferByteSizePerSocket: Long,
    override val socketPrefix: String,
    override val socketWaitTimeoutSeconds: Int,
    override val devNullAfterDeserialization: Boolean,
    val skipUpload: Boolean,
    val useGarbagePart: Boolean,
    override val skipJsonOnProto: Boolean,
    override val disableUUID: Boolean,
    override val disableMapper: Boolean,
    override val useCodedInputStream: Boolean = false,
    override val useSnappy: Boolean = false,
) :
    DestinationConfiguration(),
    AzureBlobStorageClientConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T>,
    SocketTestConfig {
    // for now, we're not exposing this as a user-configurable option
    // so just return a hardcoded default path config
    override val objectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = "",
            // This is equivalent to the default,
            // but is nicer for tests,
            // and also matches user intuition more closely.
            // The default puts the `<date>_<epoch>_` into the path format,
            // which is (a) confusing, and (b) makes the file transfer tests more annoying.
            pathPattern = "\${NAMESPACE}/\${STREAM_NAME}/",
            fileNamePattern = "{date}_{timestamp}_{part_number}{format_extension}",
        )

    override val generationIdMetadataKey = GENERATION_ID_METADATA_KEY_OVERRIDE
}

@Singleton
class AzureBlobStorageConfigurationFactory :
    DestinationConfigurationFactory<
        AzureBlobStorageSpecification, AzureBlobStorageConfiguration<*>> {
    override fun makeWithoutExceptionHandling(
        pojo: AzureBlobStorageSpecification
    ): AzureBlobStorageConfiguration<*> {
        val azureBlobStorageClientConfiguration = pojo.toAzureBlobStorageClientConfiguration()
        azureBlobStorageClientConfiguration.endpointDomainName =
            pojo.azureBlobStorageEndpointDomainName
        azureBlobStorageClientConfiguration.spillSize = pojo.azureBlobStorageSpillSize
        return AzureBlobStorageConfiguration(
            azureBlobStorageClientConfiguration = azureBlobStorageClientConfiguration,
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
            objectStorageCompressionConfiguration =
                ObjectStorageCompressionConfiguration(NoopProcessor),
            numSockets = pojo.numSockets ?: 2,
            numUploadWorkers = pojo.numPartLoaders ?: 10,
            numPartWorkers = pojo.numPartFormatters ?: pojo.numSockets ?: 2,
            inputSerializationFormat = pojo.inputSerializationFormat
                ?: DestinationConfiguration.InputSerializationFormat.FLATBUFFERS,
            partSizeBytes = (pojo.partSizeMb ?: 10) * 1024L * 1024L,
            maxMemoryRatioReservedForParts = pojo.maxMemoryRatioReservedForParts ?: 1.0,
            inputBufferByteSizePerSocket = pojo.inputBufferByteSizePerSocket ?: (16384),
            socketPrefix = pojo.socketPrefix
                ?: "/Users/jschmidt/.sockets/ab_socket_", // "/var/run/sockets/ab_socket_",
            socketWaitTimeoutSeconds = pojo.socketWaitTimeoutSeconds ?: 60,
            devNullAfterDeserialization = pojo.devNullAfterDeserialization ?: false,
            skipUpload = pojo.skipUpload ?: false,
            useGarbagePart = pojo.useGarbagePart ?: false,
            skipJsonOnProto = pojo.skipJsonOnProto ?: true,
            disableUUID = pojo.disableUUID ?: false,
            disableMapper = pojo.disableMapper ?: false,
            useCodedInputStream = pojo.useCodedInputStream ?: true,
            useSnappy = pojo.useSnappy ?: false,
        )
    }
}

@Suppress("UNCHECKED_CAST")
@Factory
class AzureBlobStorageConfigurationProvider<T : OutputStream>(
    private val config: DestinationConfiguration
) {
    @Singleton
    fun get(): AzureBlobStorageConfiguration<T> {
        return config as AzureBlobStorageConfiguration<T>
    }
}
