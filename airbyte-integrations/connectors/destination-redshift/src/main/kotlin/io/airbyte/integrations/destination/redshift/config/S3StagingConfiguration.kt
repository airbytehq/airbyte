/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.config

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Sealed interface for uploading method configuration. Uses Jackson polymorphic type handling to
 * produce a `oneOf` JSON schema with `method` as the discriminator property.
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "method",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = S3StagingConfiguration::class, name = "S3 Staging"),
)
sealed interface UploadingMethod

/** S3 staging configuration for uploading data to Redshift via S3 COPY. */
@JsonSchemaTitle("AWS S3 Staging")
@JsonIgnoreProperties(ignoreUnknown = true)
data class S3StagingConfiguration(
    @JsonProperty("method") val method: String = "S3 Staging",
    @JsonProperty("s3_bucket_name")
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription(
        "\"Enter the name of the <a href=\\\"https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html\\\">staging S3 bucket</a>."
    )
    @get:JsonSchemaInject(json = """{"order": 0, "examples":["airbyte.staging"]}""")
    val s3BucketName: String = "",
    @JsonProperty("s3_bucket_path")
    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "The directory under the S3 bucket where data will be written. If not provided, then defaults to the root directory. See <a href=\"https://docs.aws.amazon.com/prescriptive-guidance/latest/defining-bucket-names-data-lakes/faq.html#:~:text=be%20globally%20unique.-,For%20S3%20bucket%20paths,-%2C%20you%20can%20use\">path's name recommendations</a> for more details."
    )
    @get:JsonSchemaInject(json = """{"order": 1, "examples":["data_sync/test"]}""")
    val s3BucketPath: String? = null,
    @JsonProperty("s3_bucket_region")
    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription("Enter the region of the S3 staging bucket")
    @get:JsonSchemaInject(
        json =
            """{"order": 2, "default": "", "enum": ["", "af-south-1", "ap-east-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3", "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ca-central-1", "ca-west-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2", "eu-west-1", "eu-west-2", "eu-west-3", "il-central-1", "me-central-1", "me-south-1", "sa-east-1", "us-east-1", "us-east-2", "us-gov-east-1", "us-gov-west-1", "us-west-1", "us-west-2"]}"""
    )
    val s3BucketRegion: String = "",
    @JsonProperty("access_key_id")
    @get:JsonSchemaTitle("S3 Access Key Id")
    @get:JsonPropertyDescription(
        "This ID grants access to the above S3 staging bucket. Airbyte requires Read and Write permissions to the given bucket. See <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">AWS docs</a> on how to generate an access key ID and secret access key."
    )
    @get:JsonSchemaInject(json = """{"order": 3, "airbyte_secret": true}""")
    val accessKeyId: String = "",
    @JsonProperty("secret_access_key")
    @get:JsonSchemaTitle("S3 Secret Access Key")
    @get:JsonPropertyDescription(
        "The corresponding secret to the above access key id. See <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">AWS docs</a> on how to generate an access key ID and secret access key."
    )
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    val secretAccessKey: String = "",
    @JsonProperty("file_name_pattern")
    @get:JsonSchemaTitle("S3 Filename pattern")
    @get:JsonPropertyDescription(
        "The pattern allows you to set the file-name format for the S3 staging file(s)"
    )
    @get:JsonSchemaInject(
        json =
            """{"order": 5, "examples":["{date}", "{date:yyyy_MM}", "{timestamp}", "{part_number}", "{sync_id}"]}"""
    )
    val fileNamePattern: String? = null,
    @JsonProperty("purge_staging_data")
    @get:JsonSchemaTitle("Purge Staging Files and Tables")
    @get:JsonPropertyDescription(
        "Whether to delete the staging files from S3 after completing the sync. See <a href=\"https://docs.airbyte.com/integrations/destinations/redshift/#:~:text=the%20root%20directory.-,Purge%20Staging%20Data,-Whether%20to%20delete\"> docs</a> for details."
    )
    @get:JsonSchemaInject(json = """{"order": 6, "default": true}""")
    val purgeStagingData: Boolean? = true,
) : UploadingMethod
