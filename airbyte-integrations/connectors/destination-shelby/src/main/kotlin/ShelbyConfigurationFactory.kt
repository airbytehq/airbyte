package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSArnRoleConfiguration
import io.airbyte.cdk.load.command.object_storage.GZIPCompressionSpecification
import io.airbyte.cdk.load.command.object_storage.NoCompressionSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionConfiguration
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.command.s3.S3BucketConfiguration
import io.airbyte.cdk.load.file.GZIPProcessor
import io.airbyte.cdk.load.file.NoopProcessor
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStream

@Singleton
class ShelbyConfigurationFactory :
    DestinationConfigurationFactory<ShelbySpecification, ShelbyConfiguration<*>> {
    override fun makeWithoutExceptionHandling(pojo: ShelbySpecification): ShelbyConfiguration<*> =
        ShelbyConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            awsArnRoleConfiguration = pojo.toAWSArnRoleConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            objectStoragePathConfiguration = pojo.toObjectStoragePathConfiguration(),
            objectStorageCompressionConfiguration = pojo.toCompressionConfiguration(),
        )
}
