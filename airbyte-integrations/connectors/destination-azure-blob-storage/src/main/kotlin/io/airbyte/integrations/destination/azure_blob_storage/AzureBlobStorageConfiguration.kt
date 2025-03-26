/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.azureBlobStorage.BaseAzureBlobStorageConfiguration
import io.airbyte.cdk.load.command.azureBlobStorage.BaseAzureBlobStorageConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

class AzureBlobStorageConfiguration(
    // Client-facing configuration
    override val baseAzureBlobStorageConfiguration: BaseAzureBlobStorageConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = 1,
    override val estimatedRecordMemoryOverheadRatio: Double = 5.0,
    override val processEmptyFiles: Boolean = true,
    val numPartWorkers: Int = 2,
    val numUploadWorkers: Int = 5,
    val maxMemoryRatioReservedForParts: Double = 0.4,
    val objectSizeBytes: Long = 200L * 1024 * 1024,
    val partSizeBytes: Long = 10L * 1024 * 1024,
) :
    DestinationConfiguration(),
    BaseAzureBlobStorageConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider

@Singleton
class AzureBlobStorageConfigurationFactory :
    DestinationConfigurationFactory<AzureBlobStorageSpecification, AzureBlobStorageConfiguration> {
    override fun makeWithoutExceptionHandling(
        pojo: AzureBlobStorageSpecification
    ): AzureBlobStorageConfiguration {
        return AzureBlobStorageConfiguration(
            baseAzureBlobStorageConfiguration = pojo.toBaseAzureBlobStorageConfiguration(),
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
        )
    }
}

@Suppress("UNCHECKED_CAST")
@Factory
class S3V2ConfigurationProvider<T : OutputStream>(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): AzureBlobStorageConfiguration {
        return config as AzureBlobStorageConfiguration
    }
}
