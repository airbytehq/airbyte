/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import com.amazonaws.auth.AWSCredentialsProvider
import io.airbyte.cdk.load.command.AWSCredentialsProviderSupplier
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.OutputFormatConfiguration
import io.airbyte.cdk.load.command.OutputFormatConfigurationProvider
import io.airbyte.cdk.load.command.S3BucketConfiguration
import io.airbyte.cdk.load.command.S3BucketConfigurationProvider
import io.airbyte.cdk.load.command.StoragePathConfiguration
import io.airbyte.cdk.load.command.StoragePathConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class S3V2Configuration(
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val awsCredentialProvider: AWSCredentialsProvider,
    override val outputFormat: OutputFormatConfiguration,
    override val pathConfiguration: StoragePathConfiguration,
) :
    AWSCredentialsProviderSupplier,
    S3BucketConfigurationProvider,
    OutputFormatConfigurationProvider,
    StoragePathConfigurationProvider,
    DestinationConfiguration()

@Singleton
class S3V2ConfigurationFactory :
    DestinationConfigurationFactory<S3V2Specification, S3V2Configuration> {
    override fun makeWithoutExceptionHandling(pojo: S3V2Specification): S3V2Configuration {
        return S3V2Configuration(
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            awsCredentialProvider = pojo.toAWSCredentialsProvider(),
            outputFormat = pojo.toOutputFormatConfiguration(),
            pathConfiguration = pojo.toStoragePathConfiguration()
        )
    }
}

/** This allows micronaut to inject the simplified configuration into the implementation. */
@Factory
class S3V2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3V2Configuration {
        return config as S3V2Configuration
    }
}
