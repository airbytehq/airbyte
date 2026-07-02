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

// Tuned ObjectLoader defaults, rebumped from the CDK/S3 baseline (numPartWorkers 2->4,
// numUploadWorkers 5->8, numUploadCompleters 1->2). numPartWorkers is the Avro+snappy encoding
// (CPU) lever; benchmarks showed the others give marginal gains. Not user-editable — the GA
// object-storage destinations likewise ship fixed defaults rather than tuning knobs.
private const val DEFAULT_NUM_PART_WORKERS = 4
private const val DEFAULT_NUM_UPLOAD_WORKERS = 8
private const val DEFAULT_NUM_UPLOAD_COMPLETERS = 2
private const val DEFAULT_NUM_PROCESS_RECORDS_WORKERS = 1
private const val DEFAULT_OBJECT_SIZE_BYTES = 200L * 1024 * 1024
private const val DEFAULT_PART_SIZE_BYTES = 20L * 1024 * 1024

/**
 * Mirror of S3V2Configuration. Differences from S3:
 * - Implements [GcsClientConfigurationProvider] (NOT S3BucketConfigurationProvider /
 * AWS*ConfigurationProvider). This is the ONE bean [io.airbyte.cdk.load.file.gcs.GcsClientFactory]
 * needs to build the GcsS3Client. The AWS access-key / arn-role providers are synthesized
 * internally by GcsClientFactory from the HMAC credentials, so the config does not expose them.
 * - partSizeBytes / objectSizeBytes MUST be GCS-S3-interop safe. Because GcsS3Client delegates to
 * the real S3 multipart streaming upload against storage.googleapis.com, S3 multipart rules apply
 * (>= 5MB parts). Keeping S3's 20MB part / 200MB object also matches the v0.4.x ~200MB file target.
 * Do NOT assume GCS resumable 256KB-multiple rules here — that only applies to the (currently
 * unused) native GcsNativeClient path.
 */
data class GcsV2Configuration<T : OutputStream>(
    // Client-facing configuration
    override val gcsClientConfiguration: GcsClientConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration,
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,

    // Internal configuration
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration(),
    override val numProcessRecordsWorkers: Int = DEFAULT_NUM_PROCESS_RECORDS_WORKERS,

    // ObjectLoader-specific tuned defaults (rebumped from the CDK's 2/5 baseline).
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
            // Tuned ObjectLoader defaults (not user-editable), mirroring how the GA object-storage
            // destinations ship fixed defaults. maxMemoryRatio auto-selects by stream kind; in
            // SOCKET
            // mode the CDK re-derives part size and upload parallelism from the socket count.
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
