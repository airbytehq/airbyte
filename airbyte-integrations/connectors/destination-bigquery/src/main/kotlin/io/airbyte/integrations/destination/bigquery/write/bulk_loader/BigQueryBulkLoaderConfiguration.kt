/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.gcs.GcsHmacKeyConfiguration
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider.Companion.getNoCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream

data class BigqueryBulkLoadConfiguration(
    val bigQueryConfiguration: BigqueryConfiguration,
) :
    ObjectStoragePathConfigurationProvider,
    ObjectStorageFormatConfigurationProvider,
    ObjectStorageUploadConfigurationProvider,
    S3BucketConfigurationProvider,
    AWSAccessKeyConfigurationProvider,
    AWSArnRoleConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<ByteArrayOutputStream> {
    override val objectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = "",
            // This is equivalent to the default,
            // but is nicer for tests,
            // and also matches user intuition more closely.
            // The default puts the `<date>_<epoch>_` into the path format,
            // which is (a) confusing, and (b) makes the file transfer tests more annoying.
            // TODO: This is unverified. We need to understand what the current behavior is
            pathPattern = "\${NAMESPACE}/\${STREAM_NAME}/",
            fileNamePattern = "{date}_{timestamp}_{part_number}{format_extension}",
        )
    override val objectStorageFormatConfiguration: ObjectStorageFormatConfiguration =
        CSVFormatConfiguration()
    override val objectStorageUploadConfiguration: ObjectStorageUploadConfiguration =
        ObjectStorageUploadConfiguration()
    override val objectStorageCompressionConfiguration:
        ObjectStorageCompressionConfiguration<ByteArrayOutputStream> =
        getNoCompressionConfiguration()
    override val s3BucketConfiguration: S3BucketConfiguration
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration = AWSArnRoleConfiguration(null)

    init {
        bigQueryConfiguration.loadingMethod as GcsStagingConfiguration
        s3BucketConfiguration =
            S3BucketConfiguration(
                s3BucketName = bigQueryConfiguration.loadingMethod.gcsClientConfig.gcsBucketName,
                s3BucketRegion = bigQueryConfiguration.loadingMethod.gcsClientConfig.region?.region,
                s3Endpoint = "https://storage.googleapis.com",
            )
        val credentials =
            bigQueryConfiguration.loadingMethod.gcsClientConfig.credential
                as GcsHmacKeyConfiguration
        awsAccessKeyConfiguration =
            AWSAccessKeyConfiguration(
                accessKeyId = credentials.accessKeyId,
                secretAccessKey = credentials.secretAccessKey
            )
    }
}

@Factory
@Requires(condition = BigqueryConfiguredForBulkLoad::class)
class BigqueryBLConfigurationProvider(private val config: BigqueryConfiguration) {
    @Singleton fun get() = BigqueryBulkLoadConfiguration(config)
}
