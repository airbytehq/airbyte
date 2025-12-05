package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfigurationProvider
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfig
import io.airbyte.cdk.load.command.dlq.ObjectStorageConfigProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatConfigurationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfigurationProvider
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfigurationProvider
import java.io.OutputStream

data class ShelbyConfiguration(
    override val objectStorageConfig: ObjectStorageConfig,
) : DestinationConfiguration(),
    ObjectStorageConfigProvider
