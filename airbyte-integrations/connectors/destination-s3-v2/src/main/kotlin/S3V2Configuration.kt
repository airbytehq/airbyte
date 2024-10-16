/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data class S3V2Configuration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    S3BucketConfigurationProvider,
    ObjectStoragePathConfigurationProvider

@Singleton
class S3V2ConfigurationFactory :
    DestinationConfigurationFactory<S3V2Specification, S3V2Configuration> {
    override fun makeWithoutExceptionHandling(pojo: S3V2Specification): S3V2Configuration {
        return S3V2Configuration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            objectStoragePathConfiguration = pojo.toObjectStoragePathConfiguration()
        )
    }
}

@Factory
class S3V2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3V2Configuration {
        return config as S3V2Configuration
    }
}
