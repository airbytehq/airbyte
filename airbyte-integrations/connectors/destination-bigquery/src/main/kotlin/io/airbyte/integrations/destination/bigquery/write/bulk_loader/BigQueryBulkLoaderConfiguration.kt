/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.avro.AvroCompressionConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GOOGLE_STORAGE_ENDPOINT
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.object_storage.AvroFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.integrations.destination.bigquery.copy.BigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.copy.DisabledBigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingFileFormat
import java.io.BufferedOutputStream
import java.io.ByteArrayOutputStream
import org.apache.avro.file.CodecFactory

data class BigqueryBulkLoadConfiguration(
    val bigQueryConfiguration: BigqueryConfiguration,
    val stagesAvroFiles: Boolean,
) :
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    S3BucketConfigurationProvider,
    AWSAccessKeyConfigurationProvider,
    AWSArnRoleConfigurationProvider,
    GcsClientConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<BufferedOutputStream> {
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration =
        if (stagesAvroFiles) {
            // The writer sets the codec; this value only names the files' extension.
            AvroFormatConfiguration(
                avroCompressionConfiguration =
                    AvroCompressionConfiguration(CodecFactory.snappyCodec()),
            )
        } else {
            CSVFormatConfiguration(rootLevelFlattening = !bigQueryConfiguration.legacyRawTablesOnly)
        }
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration()
    override val s3BucketConfiguration: S3BucketConfiguration
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration = AWSArnRoleConfiguration(null)
    override val gcsClientConfiguration: GcsClientConfiguration =
        (bigQueryConfiguration.loadingMethod as GcsStagingConfiguration).gcsClientConfig
    override val objectStorageCompressionConfiguration =
        ObjectStorageCompressionConfiguration(
            if (stagesAvroFiles) UncompressedProcessor else GZIPProcessor,
        )

    init {
        bigQueryConfiguration.loadingMethod as GcsStagingConfiguration
        s3BucketConfiguration =
            S3BucketConfiguration(
                s3BucketName = bigQueryConfiguration.loadingMethod.gcsClientConfig.gcsBucketName,
                s3BucketRegion = bigQueryConfiguration.loadingMethod.gcsClientConfig.region,
                s3Endpoint = GOOGLE_STORAGE_ENDPOINT,
            )
        val credentials =
            bigQueryConfiguration.loadingMethod.gcsClientConfig.credential
                as GcsHmacKeyConfiguration
        awsAccessKeyConfiguration =
            AWSAccessKeyConfiguration(
                accessKeyId = credentials.accessKeyId,
                secretAccessKey = credentials.secretAccessKey,
            )

        objectStoragePathConfiguration =
            ObjectStoragePathConfiguration(
                prefix = bigQueryConfiguration.loadingMethod.gcsClientConfig.path,
                pathPattern =
                    "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${UUID}",
                fileNamePattern = "{date}_{timestamp}_{part_number}{format_extension}",
                resolveNamesMethod = { Transformations.toAlphanumericAndUnderscore(it) },
            )
    }
}

/**
 * Avro staging files, in the GCS staging loading method outside legacy raw tables mode, where every
 * column of the table is a column of the file.
 */
val BigqueryConfiguration.stagesAvroFiles: Boolean
    get() =
        !legacyRawTablesOnly &&
            (loadingMethod as? GcsStagingConfiguration)?.fileFormat == GcsStagingFileFormat.AVRO

/**
 * The Fusion load-input archive copies every staged object as it is, and its consumers read gzipped
 * CSV, so staging stays CSV while the archive is enabled.
 */
fun BigqueryConfiguration.stagesAvroFiles(archive: BigqueryS3Copy): Boolean =
    stagesAvroFiles && archive is DisabledBigqueryS3Copy

/** Avro files compress their own blocks; a second layer would only cost CPU. */
data object UncompressedProcessor : StreamProcessor<BufferedOutputStream> {
    override val wrapper: (ByteArrayOutputStream) -> BufferedOutputStream = {
        BufferedOutputStream(it)
    }
    override val partFinisher: BufferedOutputStream.() -> Unit = { close() }
    override val extension: String? = null
}
