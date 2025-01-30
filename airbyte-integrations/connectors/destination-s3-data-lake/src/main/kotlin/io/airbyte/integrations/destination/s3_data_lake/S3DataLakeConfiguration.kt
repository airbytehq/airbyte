/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Inject
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_NAMESPACE = "airbyte_test_namespace"
const val TEST_TABLE = "airbyte_test_table"

data class S3DataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    override val numProcessRecordsWorkers: Int,
    override val numProcessBatchWorkers: Int,
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider

@Singleton
// primary constructor is used by tests
class S3DataLakeConfigurationFactory(private val anyStreamIsDedup: Boolean) :
    DestinationConfigurationFactory<S3DataLakeSpecification, S3DataLakeConfiguration> {
    // micronaut uses this constructor to instantiate the bean
    @Inject
    constructor(catalog: DestinationCatalog) : this(catalog.streams.any { it.importType is Dedupe })

    override fun makeWithoutExceptionHandling(
        pojo: S3DataLakeSpecification
    ): S3DataLakeConfiguration {
        return S3DataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
            // When running in dedup mode, we need to process everything in serial,
            // so that we don't overwrite newer records with older records.
            numProcessRecordsWorkers =
                if (anyStreamIsDedup) {
                    1
                } else {
                    2
                },
            numProcessBatchWorkers =
                if (anyStreamIsDedup) {
                    1
                } else {
                    5
                },
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
