package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import java.io.OutputStream

data class ShelbyConfiguration<T : OutputStream>(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val awsArnRoleConfiguration: AWSArnRoleConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val objectStoragePathConfiguration: ObjectStoragePathConfiguration,
    override val objectStorageCompressionConfiguration: ObjectStorageCompressionConfiguration<T>,
) : DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    AWSArnRoleConfigurationProvider,
    S3BucketConfigurationProvider,
    ObjectStoragePathConfigurationProvider,
    ObjectStorageCompressionConfigurationProvider<T>
