/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

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

data class GcsDataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    override val numProcessRecordsWorkers: Int,
    override val numProcessBatchWorkers: Int,
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider {
    override val recordBatchSizeBytes: Long
        get() = 1500 * 1024 * 1024
}

@Singleton
class GcsDataLakeConfigurationFactory :
    DestinationConfigurationFactory<GcsDataLakeSpecification, GcsDataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: GcsDataLakeSpecification
    ): GcsDataLakeConfiguration {
        return GcsDataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
            // When running in dedup mode, we need to process everything in serial,
            // so that we don't overwrite newer records with older records.
            // For the sake of simplicity, just set workers to 1 regardless of
            // sync mode.
            numProcessRecordsWorkers = 1,
            numProcessBatchWorkers = 1,
        )
    }
}

@Factory
class S3DataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): GcsDataLakeConfiguration {
        return config as GcsDataLakeConfiguration
    }
}
