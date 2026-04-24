/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/** Reusable S3 staging configuration for destinations that stage data via S3. */
@JsonIgnoreProperties(ignoreUnknown = true)
data class S3StagingConfiguration(
    @JsonProperty("method") val method: String = "S3 Staging",
    @JsonProperty("s3_bucket_name")
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription(
        "Enter the name of the <a href=\"https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html\">staging S3 bucket</a>. This bucket will be used to stage data before loading it into Redshift."
    )
    @get:JsonSchemaInject(
        json = """{"order": 1, "examples":["airbyte-staging-bucket"]}"""
    )
    val s3BucketName: String = "",
    @JsonProperty("s3_bucket_path")
    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "The directory under the S3 bucket where staging data will be written. If not provided, defaults to the root directory."
    )
    @get:JsonSchemaInject(
        json = """{"order": 2, "examples":["data_sync/redshift"]}"""
    )
    val s3BucketPath: String? = null,
    @JsonProperty("s3_bucket_region")
    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription(
        "The region of the S3 staging bucket. Place the S3 bucket and the Redshift cluster in the same region to reduce networking costs."
    )
    @get:JsonSchemaInject(
        json = """{"order": 3, "examples":["us-east-1"]}"""
    )
    val s3BucketRegion: String? = "",
    @JsonProperty("access_key_id")
    @get:JsonSchemaTitle("S3 Access Key ID")
    @get:JsonPropertyDescription(
        "Enter your <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">AWS Access Key ID</a>. Airbyte requires read and write <a href=\"https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html\">permissions</a> to objects in the staging bucket."
    )
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    val accessKeyId: String = "",
    @JsonProperty("secret_access_key")
    @get:JsonSchemaTitle("S3 Secret Access Key")
    @get:JsonPropertyDescription(
        "Enter the corresponding <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">AWS Secret Access Key</a> for the Access Key ID."
    )
    @get:JsonSchemaInject(json = """{"order": 5, "airbyte_secret": true}""")
    val secretAccessKey: String = "",
    @JsonProperty("file_name_pattern")
    @get:JsonSchemaTitle("S3 Filename Pattern")
    @get:JsonPropertyDescription(
        "The pattern for S3 staging file names. Supported placeholders: {date}, {date:yyyy_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part_number}, {sync_id}, {format_extension}."
    )
    @get:JsonSchemaInject(json = """{"order": 6}""")
    val fileNamePattern: String? = null,
    @JsonProperty("purge_staging_data")
    @get:JsonSchemaTitle("Purge Staging Files")
    @get:JsonPropertyDescription(
        "Whether to delete staging files from S3 after completing the sync. Set to false if you want to retain staging files for debugging or auditing. Default: true."
    )
    @get:JsonSchemaInject(json = """{"order": 7, "default": true}""")
    val purgeStagingData: Boolean? = true,
)
