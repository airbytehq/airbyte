/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.spec

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/** Reusable S3 staging configuration for destinations that stage data via S3. */
@JsonIgnoreProperties(ignoreUnknown = true)
data class S3StagingConfiguration(
    @JsonProperty("method") val method: String = "S3 Staging",
    @JsonProperty("s3_bucket_name")
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription("The name of the staging S3 bucket.")
    val s3BucketName: String = "",
    @JsonProperty("s3_bucket_path")
    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription("The directory under the S3 bucket where data will be written.")
    val s3BucketPath: String? = null,
    @JsonProperty("s3_bucket_region")
    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription("The region of the S3 staging bucket.")
    val s3BucketRegion: String? = "",
    @JsonProperty("access_key_id")
    @get:JsonSchemaTitle("S3 Access Key Id")
    @get:JsonPropertyDescription("AWS Access Key ID for S3 access.")
    val accessKeyId: String = "",
    @JsonProperty("secret_access_key")
    @get:JsonSchemaTitle("S3 Secret Access Key")
    @get:JsonPropertyDescription("AWS Secret Access Key for S3 access.")
    val secretAccessKey: String = "",
    @JsonProperty("file_name_pattern")
    @get:JsonSchemaTitle("S3 Filename Pattern")
    @get:JsonPropertyDescription("The pattern for S3 staging file names.")
    val fileNamePattern: String? = null,
    @JsonProperty("purge_staging_data")
    @get:JsonSchemaTitle("Purge Staging Files")
    @get:JsonPropertyDescription("Whether to delete staging files from S3 after sync.")
    val purgeStagingData: Boolean? = true,
)
