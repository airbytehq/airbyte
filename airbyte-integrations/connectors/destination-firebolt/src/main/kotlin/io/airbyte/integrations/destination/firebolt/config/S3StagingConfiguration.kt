/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.config

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/** S3 staging configuration for uploading data to Firebolt via COPY FROM. */
@JsonSchemaTitle("AWS S3 Staging")
@JsonIgnoreProperties(ignoreUnknown = true)
data class S3StagingConfiguration(
    @JsonProperty("s3_bucket_name")
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription("Enter the name of the S3 staging bucket.")
    @get:JsonSchemaInject(json = """{"order": 0, "examples":["airbyte.staging"]}""")
    val s3BucketName: String = "",
    @JsonProperty("s3_bucket_path")
    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "The directory under the S3 bucket where data will be written. If not provided, defaults to the root directory."
    )
    @get:JsonSchemaInject(json = """{"order": 1, "examples":["data_sync/test"]}""")
    val s3BucketPath: String? = null,
    @JsonProperty("s3_bucket_region")
    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription("Enter the region of the S3 staging bucket.")
    @get:JsonSchemaInject(
        json =
            """{"order": 2, "default": "", "enum": ["", "af-south-1", "ap-east-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3", "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ca-central-1", "ca-west-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2", "eu-west-1", "eu-west-2", "eu-west-3", "il-central-1", "me-central-1", "me-south-1", "sa-east-1", "us-east-1", "us-east-2", "us-gov-east-1", "us-gov-west-1", "us-west-1", "us-west-2"]}"""
    )
    val s3BucketRegion: String = "",
    @JsonProperty("access_key_id")
    @get:JsonSchemaTitle("S3 Access Key Id")
    @get:JsonPropertyDescription(
        "The access key ID for the S3 staging bucket. Airbyte requires Read and Write permissions."
    )
    @get:JsonSchemaInject(json = """{"order": 3, "airbyte_secret": true}""")
    val accessKeyId: String = "",
    @JsonProperty("secret_access_key")
    @get:JsonSchemaTitle("S3 Secret Access Key")
    @get:JsonPropertyDescription("The corresponding secret for the S3 access key.")
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true}""")
    val secretAccessKey: String = "",
    @JsonProperty("file_name_pattern")
    @get:JsonSchemaTitle("S3 Filename pattern")
    @get:JsonPropertyDescription("Pattern for naming S3 staging files.")
    @get:JsonSchemaInject(
        json =
            """{"order": 5, "examples":["{date}", "{timestamp}", "{part_number}", "{sync_id}"]}"""
    )
    val fileNamePattern: String? = null,
    @JsonProperty("purge_staging_data")
    @get:JsonSchemaTitle("Purge Staging Files and Tables")
    @get:JsonPropertyDescription(
        "Whether to delete the staging files from S3 after completing the sync."
    )
    @get:JsonSchemaInject(json = """{"order": 6, "default": true}""")
    val purgeStagingData: Boolean? = true,
)
