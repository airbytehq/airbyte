package io.airbyte.integrations.destination.shelby

import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.aws.AWSArnRoleSpecification
import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
import io.airbyte.cdk.load.command.s3.S3PathSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Shelby Goes Fast")
@JsonSchemaInject
class ShelbySpecification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    AWSArnRoleSpecification,
    S3BucketSpecification,
    S3PathSpecification,
    ObjectStorageCompressionSpecificationProvider,
    ObjectStorageFormatSpecificationProvider
{
    @get:JsonSchemaInject(
        json =
        """{"examples":["A012345678910EXAMPLE"],"airbyte_secret": true,"always_show": true,"order":0}"""
    )
    override val accessKeyId: String? = null

    @get:JsonSchemaInject(
        json =
        """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],"airbyte_secret": true,"always_show": true,"order":1}"""
    )
    override val secretAccessKey: String? = null

    @get:JsonSchemaInject(
        json =
        """{"examples":["arn:aws:iam::123456789:role/ExternalIdIsYourWorkspaceId"],"order":2}"""
    )
    override val roleArn: String? = null

    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":3}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"],"order":4}""")
    override val s3BucketPath: String = ""

    @get:JsonSchemaInject(json = """{"examples":["us-east-1"],"order":5,"default":""}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"examples":["http://localhost:9000"],"order":6}""")
    override val s3Endpoint: String? = null

    @get:JsonSchemaInject(
        json =
        "{\"examples\":[\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"],\"order\":7}"
    )
    override val s3PathFormat: String? = null

    @get:JsonSchemaInject(
        json =
        "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"],\"order\":8}"
    )
    override val fileNamePattern: String? = null

    @get:JsonSchemaInject(json = """{"order":9}""")
    override val format: ObjectStorageFormatSpecification = CSVFormatSpecification()

    @get:JsonSchemaInject(json = """{"order":10}""")
    override val compression: ObjectStorageCompressionSpecification? = null
}

@Singleton
class ShelbySpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
