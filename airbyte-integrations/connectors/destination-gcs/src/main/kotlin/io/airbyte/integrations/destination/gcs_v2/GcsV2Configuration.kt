/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.OutputStream

private const val DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.4
private const val FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS = 0.2

// Tuned ObjectLoader defaults (not user-editable).
private const val DEFAULT_NUM_PART_WORKERS = 4
private const val DEFAULT_NUM_UPLOAD_WORKERS = 8
private const val DEFAULT_NUM_UPLOAD_COMPLETERS = 2
private const val DEFAULT_NUM_PROCESS_RECORDS_WORKERS = 1
private const val DEFAULT_OBJECT_SIZE_BYTES = 200L * 1024 * 1024
private const val DEFAULT_PART_SIZE_BYTES = 20L * 1024 * 1024

/** Connector configuration holding GCS client, path, format, compression, and upload settings. */
data class GcsV2Configuration<T : OutputStream>(
    override val gcsClientConfiguration: GcsClientConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = DEFAULT_NUM_PROCESS_RECORDS_WORKERS,
    val numPartWorkers: Int = DEFAULT_NUM_PART_WORKERS,
    val numUploadWorkers: Int = DEFAULT_NUM_UPLOAD_WORKERS,
    val numUploadCompleters: Int = DEFAULT_NUM_UPLOAD_COMPLETERS,
    val maxMemoryRatioReservedForParts: Double = DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS,
    val objectSizeBytes: Long = DEFAULT_OBJECT_SIZE_BYTES,
    val partSizeBytes: Long = DEFAULT_PART_SIZE_BYTES,
) :
    DestinationConfiguration(),
    GcsClientConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T>

@Singleton
class GcsV2ConfigurationFactory(private val destinationCatalog: DestinationCatalog) :
    DestinationConfigurationFactory<GcsV2Specification, GcsV2Configuration<*>> {
    override fun makeWithoutExceptionHandling(pojo: GcsV2Specification): GcsV2Configuration<*> {
        return GcsV2Configuration(
            gcsClientConfiguration =
                GcsClientConfiguration(
                    commonSpecification = pojo,
                    regionSpecification = pojo.gcsBucketRegion ?: GcsRegion.US,
                ),
            objectStoragePathConfiguration = pojo.toObjectStoragePathConfiguration(),
            objectStorageFormatConfiguration = pojo.toObjectStorageFormatConfiguration(),
            objectStorageCompressionConfiguration = pojo.toCompressionConfiguration(),
            numPartWorkers = DEFAULT_NUM_PART_WORKERS,
            numUploadWorkers = DEFAULT_NUM_UPLOAD_WORKERS,
            numUploadCompleters = DEFAULT_NUM_UPLOAD_COMPLETERS,
            numProcessRecordsWorkers = DEFAULT_NUM_PROCESS_RECORDS_WORKERS,
            objectSizeBytes = DEFAULT_OBJECT_SIZE_BYTES,
            partSizeBytes = DEFAULT_PART_SIZE_BYTES,
            maxMemoryRatioReservedForParts =
                if (destinationCatalog.streams.any { it.isFileBased }) {
                    FILE_DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                } else {
                    DEFAULT_MAX_MEMORY_RESERVED_FOR_PARTS
                },
        )
    }
}

@Suppress("UNCHECKED_CAST")
@Factory
class GcsV2ConfigurationProvider<T : OutputStream>(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): GcsV2Configuration<T> {
        return config as GcsV2Configuration<T>
    }
}
