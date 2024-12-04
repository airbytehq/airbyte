/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.NessieServerConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieServerConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_NAMESPACE = "airbyte_test_namespace"
const val TEST_TABLE = "airbyte_test_table"

data class IcebergV2Configuration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val nessieServerConfiguration: NessieServerConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    NessieServerConfigurationProvider,
    S3BucketConfigurationProvider

@Singleton
class IcebergV2ConfigurationFactory :
    DestinationConfigurationFactory<IcebergV2Specification, IcebergV2Configuration> {
    override fun makeWithoutExceptionHandling(
        pojo: IcebergV2Specification
    ): IcebergV2Configuration {
        return IcebergV2Configuration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            nessieServerConfiguration = pojo.toNessieServerConfiguration(),
        )
    }
}

@Factory
class IcebergV2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): IcebergV2Configuration {
        return config as IcebergV2Configuration
    }
}
