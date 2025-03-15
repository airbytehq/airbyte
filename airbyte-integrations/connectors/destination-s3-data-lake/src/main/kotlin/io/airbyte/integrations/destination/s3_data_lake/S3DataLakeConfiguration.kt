/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_NAMESPACE = "airbyte_test_namespace"
const val TEST_TABLE = "airbyte_test_table"

data class S3DataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    // Now that partitioning is enabled, we can run more than one worker.
    // This will likely not show performance improvements in the cloud without additional
    // resources. In the future, if enterprise or oss users need more flexibility, we can
    // expose this in their configurations.
    override val numProcessRecordsWorkers: Int = 2
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider {}

@Singleton
class S3DataLakeConfigurationFactory :
    DestinationConfigurationFactory<S3DataLakeSpecification, S3DataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: S3DataLakeSpecification
    ): S3DataLakeConfiguration {
        return S3DataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
        )
    }
}

@Factory
class S3DataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3DataLakeConfiguration {
        return config as S3DataLakeConfiguration
    }
}
