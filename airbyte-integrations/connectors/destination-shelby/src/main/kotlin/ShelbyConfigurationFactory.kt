package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import jakarta.inject.Singleton

@Singleton
class ShelbyConfigurationFactory :
    DestinationConfigurationFactory<ShelbySpecification, ShelbyConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: ShelbySpecification): ShelbyConfiguration =
        ShelbyConfiguration(
            // TODO wire from config
            awsAccessKeyConfiguration = AWSAccessKeyConfiguration(null, null),
            awsArnRoleConfiguration = AWSArnRoleConfiguration(null),
            s3BucketConfiguration = S3BucketConfiguration("yolo", null, null),
            objectStoragePathConfiguration = ObjectStoragePathConfiguration(
                prefix = "dead-letter-queue/",
                pathPattern = null,
                fileNamePattern = null,
            ),
            objectStorageCompressionConfiguration = ObjectStorageCompressionSpecificationProvider.getNoCompressionConfiguration(),
        )
}
