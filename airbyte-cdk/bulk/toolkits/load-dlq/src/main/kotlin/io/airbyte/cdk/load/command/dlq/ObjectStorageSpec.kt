/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.dlq

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.aws.AWSArnRoleSpecification
import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification

enum class ObjectStorageType(@get:JsonValue val type: String) {
    None("None"),
    S3("S3"),
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "storage_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = DisabledObjectStorageSpec::class, name = "None"),
    JsonSubTypes.Type(value = S3ObjectStorageSpec::class, name = "S3")
)
sealed interface ObjectStorageSpec {
    @get:JsonSchemaTitle("Object Storage Type")
    @get:JsonProperty("storage_type")
    val storageType: ObjectStorageType
}

class DisabledObjectStorageSpec : ObjectStorageSpec {
    override val storageType = ObjectStorageType.None
}

class S3ObjectStorageSpec :
    ObjectStorageSpec,
    ObjectStorageCompressionSpecificationProvider,
    ObjectStorageFormatSpecificationProvider,
    AWSAccessKeySpecification,
    AWSArnRoleSpecification,
    S3BucketSpecification {
    override val storageType = ObjectStorageType.S3

    @get:JsonSchemaInject(
        json =
            """{"examples":["A012345678910EXAMPLE"],"airbyte_secret": true,"always_show": true,"order":1}"""
    )
    override val accessKeyId: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],"airbyte_secret": true,"always_show": true,"order":2}"""
    )
    override val secretAccessKey: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["arn:aws:iam::123456789:role/ExternalIdIsYourWorkspaceId"],"order":3}"""
    )
    override val roleArn: String? = null

    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":4}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"examples":["us-east-1"],"order":5,"default":""}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"examples":["http://localhost:9000"],"order":6}""")
    override val s3Endpoint: String? = null

    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output.",
    )
    @get:JsonSchemaInject(json = """{"examples":["CSV","JSONL"],"order":7}""")
    @get:JsonProperty("format")
    override val format: ObjectStorageFormatSpecification = CSVFormatSpecification()

    override val compression: ObjectStorageCompressionSpecification? = null

    @get:JsonSchemaInject(json = """{"examples":["prefix/"],"order":8}""")
    @get:JsonProperty("bucket_path")
    val bucketPath: String = ""

    @get:JsonSchemaInject(
        json =
            """{"examples":["{namespace}/{stream_name}/{year}_{month}_{day}_{epoch}"],"order":9}"""
    )
    @get:JsonProperty("path_format")
    val pathFormat: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["{date}","{date:yyyy_MM}","{timestamp}","{part_number}","{sync_id}"],"order":10}"""
    )
    @get:JsonProperty("file_name_format")
    val fileNameFormat: String? = null
}
