/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_TABLE = "airbyte_test_table"

data class S3DataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    val flushBatchSizeMb: Long?,
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider {

    object Defaults {
        const val MIN_FLUSH_BATCH_SIZE_MB = 1L
        const val FLUSH_BATCH_SIZE_MB = 200L
        const val MAX_FLUSH_BATCH_SIZE_MB = 500L
    }

    val resolvedFlushBatchSizeBytes: Long
        get() {
            val mb = flushBatchSizeMb ?: Defaults.FLUSH_BATCH_SIZE_MB
            require(mb >= Defaults.MIN_FLUSH_BATCH_SIZE_MB) {
                "flush_batch_size_mb must be at least ${Defaults.MIN_FLUSH_BATCH_SIZE_MB}, got $mb"
            }
            require(mb <= Defaults.MAX_FLUSH_BATCH_SIZE_MB) {
                "flush_batch_size_mb must be at most ${Defaults.MAX_FLUSH_BATCH_SIZE_MB}, got $mb"
            }
            return mb * 1024L * 1024L
        }
}

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
            flushBatchSizeMb = pojo.flushBatchSizeMb,
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
