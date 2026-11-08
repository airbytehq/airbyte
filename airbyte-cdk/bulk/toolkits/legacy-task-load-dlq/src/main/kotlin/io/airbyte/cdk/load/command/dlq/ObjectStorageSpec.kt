/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.dlq

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.fasterxml.jackson.annotation.OptBoolean
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.aws.AWSArnRoleSpecification
import io.airbyte.cdk.load.command.azureBlobStorage.AzureBlobStorageClientSpecification
import io.airbyte.cdk.load.command.object_storage.CSVFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageCompressionSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.ObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification

abstract class ConfigurationSpecificationWithDlq(
    @get:JsonSchemaTitle("Object Storage Configuration")
    @get:JsonProperty("object_storage_config")
    val objectStorageConfig: ObjectStorageSpec? = DisabledObjectStorageSpec(),
) : ConfigurationSpecification()

enum class ObjectStorageType(@get:JsonValue val type: String) {
    None("None"),
    S3("S3"),
    AzureBlob("AzureBlob"),
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "storage_type",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = DisabledObjectStorageSpec::class, name = "None"),
    JsonSubTypes.Type(value = S3ObjectStorageSpec::class, name = "S3"),
    JsonSubTypes.Type(value = AzureBlobObjectStorageSpec::class, name = "AzureBlob"),
)
sealed interface ObjectStorageSpec {
    @get:JsonSchemaTitle("Object Storage Type")
    @get:JsonProperty("storage_type")
    val storageType: ObjectStorageType
}

class DisabledObjectStorageSpec : ObjectStorageSpec {
    override val storageType = ObjectStorageType.None
}

const val SECRET = """"airbyte_secret":true"""
const val ALWAYS_SHOW = """"always_show":true"""
const val HIDDEN = """"airbyte_hidden":true"""

class AzureBlobObjectStorageSpec :
    ObjectStorageSpec,
    AzureBlobStorageClientSpecification,
    ObjectStorageCompressionSpecificationProvider,
    ObjectStorageFormatSpecificationProvider {
    override val storageType = ObjectStorageType.AzureBlob

    @get:JsonProperty("azure_blob_storage_account_name", required = true)
    override lateinit var azureBlobStorageAccountName: String

    @get:JsonProperty("azure_blob_storage_container_name", required = true)
    override lateinit var azureBlobStorageContainerName: String

    @get:JsonSchemaTitle("Azure Blob Storage Endpoint Domain Name")
    @get:JsonProperty("azure_blob_storage_endpoint_domain_name", isRequired = OptBoolean.FALSE)
    @get:JsonSchemaInject(json = """{"default":"blob.core.windows.net"}""")
    val azureBlobStorageEndpointDomainName: String = "blob.core.windows.net"

    override val azureBlobStorageSharedAccessSignature: String? = null
    override val azureBlobStorageAccountKey: String? = null
    override val azureTenantId: String? = null
    override val azureClientId: String? = null
    override val azureClientSecret: String? = null

    @get:JsonSchemaTitle("Prefix Path in the Container")
    @get:JsonPropertyDescription("All files in the container will be prefixed by this.")
    @get:JsonProperty("bucket_path", isRequired = OptBoolean.FALSE)
    val bucketPath: String = ""

    @get:JsonSchemaTitle("Output Format")
    @get:JsonProperty("format", isRequired = OptBoolean.FALSE)
    @get:JsonSchemaInject(json = """{"default":"CSV",$HIDDEN}""")
    override val format: ObjectStorageFormatSpecification = CSVFormatSpecification()

    @get:JsonSchemaInject(json = """{$HIDDEN}""")
    override val compression: ObjectStorageCompressionSpecification? = null

    @get:JsonProperty("path_format")
    @get:JsonSchemaInject(json = """{"default":"{sync_id}/{namespace}/{stream_name}/",$HIDDEN}""")
    val pathFormat: String? = "{sync_id}/{namespace}/{stream_name}/"

    @get:JsonProperty("file_name_format")
    @get:JsonSchemaInject(
        json = """{"default":"{date}_{timestamp}_{part_number}{format_extension}",$HIDDEN}""",
    )
    val fileNameFormat: String? = "{date}_{timestamp}_{part_number}{format_extension}"
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
        json = """{"examples":["A012345678910EXAMPLE"],$SECRET,$ALWAYS_SHOW,"order":1}""",
    )
    override val accessKeyId: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],$SECRET,$ALWAYS_SHOW,"order":2}""",
    )
    override val secretAccessKey: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["arn:aws:iam::123456789:role/ExternalIdIsYourWorkspaceId"],"order":3}""",
    )
    override val roleArn: String? = null

    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":4}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"examples":["us-east-1"],"order":5,"default":""}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"examples":["http://localhost:9000"],"order":6}""")
    override val s3Endpoint: String? = null

    @get:JsonSchemaTitle("Prefix Path in the Bucket")
    @get:JsonPropertyDescription("All files in the bucket will be prefixed by this.")
    @get:JsonSchemaInject(json = """{"examples":["prefix/"],"order":7}""")
    @get:JsonProperty("bucket_path")
    val bucketPath: String = ""

    @get:JsonSchemaTitle("Output Format")
    @get:JsonPropertyDescription(
        "Format of the data output.",
    )
    @get:JsonSchemaInject(
        json =
            """{
        "examples":["CSV","JSONL"],
        "default":"CSV",
        $HIDDEN,
        "order":8
        }""",
    )
    @get:JsonProperty("format")
    override val format: ObjectStorageFormatSpecification = CSVFormatSpecification()

    @get:JsonSchemaInject(json = """{$HIDDEN}""")
    override val compression: ObjectStorageCompressionSpecification? = null

    @get:JsonSchemaInject(
        json =
            """{
                "examples":["{namespace}/{stream_name}/{year}_{month}_{day}_{epoch}"],
                "default":"{sync_id}/{namespace}/{stream_name}/",
                $HIDDEN,
                "order":10
                }""",
    )
    @get:JsonProperty("path_format")
    val pathFormat: String? = null

    @get:JsonSchemaInject(
        json =
            """{
                "examples":["{date}","{date:yyyy_MM}","{timestamp}","{part_number}","{sync_id}"],
                "default":"{date}_{timestamp}_{part_number}{format_extension}",
                $HIDDEN,
                "order":11
                }""",
    )
    @get:JsonProperty("file_name_format")
    val fileNameFormat: String? = null
}
