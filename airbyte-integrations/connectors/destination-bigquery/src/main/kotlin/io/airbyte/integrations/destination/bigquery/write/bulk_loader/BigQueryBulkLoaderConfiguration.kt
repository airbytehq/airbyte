/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GOOGLE_STORAGE_ENDPOINT
import io.airbyte.cdk.load.command.gcs.GcsClientConfiguration
import io.airbyte.cdk.load.command.gcs.GcsClientConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
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
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import java.io.BufferedOutputStream

data class BigqueryBulkLoadConfiguration(
    val bigQueryConfiguration: BigqueryConfiguration,
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
        CSVFormatConfiguration()
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration()
    override val s3BucketConfiguration: S3BucketConfiguration
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration = AWSArnRoleConfiguration(null)
    override val gcsClientConfiguration: GcsClientConfiguration =
        (bigQueryConfiguration.loadingMethod as GcsStagingConfiguration).gcsClientConfig
    override val objectStorageCompressionConfiguration =
        ObjectStorageCompressionConfiguration(GZIPProcessor)

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
                secretAccessKey = credentials.secretAccessKey
            )

        objectStoragePathConfiguration =
            ObjectStoragePathConfiguration(
                prefix = bigQueryConfiguration.loadingMethod.gcsClientConfig.path,
                pathPattern =
                    "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}/\${MONTH}/\${DAY}/\${HOUR}/\${UUID}",
                fileNamePattern = "{date}_{timestamp}_{part_number}{format_extension}",
            )
    }
}
