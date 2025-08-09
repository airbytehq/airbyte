/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
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
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.file.NoopProcessor
import io.airbyte.cdk.load.file.azureBlobStorage.GENERATION_ID_METADATA_KEY_OVERRIDE
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

private const val DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.4
private const val FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.2

class AzureBlobStorageConfiguration<T : OutputStream>(
    // Client-facing configuration
    override val azureBlobStorageClientConfiguration: AzureBlobStorageClientConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,

    // TODO remove these from config and hardcode them in AzureBlobStorageObjectLoader
    //   after we finish performance tuning
    val numPartWorkers: Int = 2,
    val numUploadWorkers: Int = 5,
    val maxMemoryRatioReservedForParts: Double = DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS,
    val objectSizeBytes: Long = 200L * 1024 * 1024,
    val partSizeBytes: Long = 10L * 1024 * 1024,
) :
    DestinationConfiguration(),
    AzureBlobStorageClientConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T> {
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
            resolveNamesMethod = { Transformations.toAzureBlobSafePath(it) },
        )

    override val generationIdMetadataKey = GENERATION_ID_METADATA_KEY_OVERRIDE
}

@Singleton
class AzureBlobStorageConfigurationFactory(private val destinationCatalog: DestinationCatalog) :
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
            maxMemoryRatioReservedForParts =
                if (destinationCatalog.streams.any { it.isFileBased }) {
                    FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                } else {
                    DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                }
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
