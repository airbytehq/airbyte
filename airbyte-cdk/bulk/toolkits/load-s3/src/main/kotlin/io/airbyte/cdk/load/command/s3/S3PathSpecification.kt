/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration

/**
 * Mix-in to provide S3 path configuration fields as properties.
 *
 * NOTE: For legacy reasons, this is unnecessarily s3-specific. Future cloud storage solutions
 * should create a single generic version of this in the `object-storage` toolkit and use that.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 */
interface S3PathSpecification {
    @get:JsonSchemaTitle("S3 Path Format")
    @get:JsonPropertyDescription(
        "Format string on how data will be organized inside the bucket directory. Read more <a href=\"https://docs.airbyte.com/integrations/destinations/s3#:~:text=The%20full%20path%20of%20the%20output%20data%20with%20the%20default%20S3%20path%20format\">here</a>"
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"]}"
    )
    @get:JsonProperty("s3_path_format")
    val s3PathFormat: String?

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern to match file names in the bucket directory. Read more <a href=\"https://docs.aws.amazon.com/AmazonS3/latest/userguide/ListingKeysUsingAPIs.html\">here</a>"
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"]}"
    )
    @get:JsonProperty("file_name_pattern")
    val fileNamePattern: String?

    @get:JsonSchemaTitle("S3 Bucket Path")
    @get:JsonPropertyDescription(
        "Directory under the S3 bucket where data will be written. Read more <a href=\"https://docs.airbyte.com/integrations/destinations/s3#:~:text=to%20format%20the-,bucket%20path,-%3A\">here</a>"
    )
    @get:JsonProperty("s3_bucket_path")
    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"]}""")
    val s3BucketPath: String

    //    Uncomment to re-enable staging

    //    @get:JsonSchemaTitle("Use a Staging Directory")
    //    @get:JsonPropertyDescription(
    //        "Whether to use a staging directory in the bucket based on the s3_staging_prefix. If
    // this is not set, airbyte will maintain sync integrity by adding metadata to each object."
    //    )
    //    @get:JsonProperty("use_staging_directory", defaultValue = "false")
    //    val useStagingDirectory: Boolean?
    //
    //    @get:JsonSchemaTitle("S3 Staging Prefix")
    //    @get:JsonPropertyDescription(
    //        "Path to use when staging data in the bucket directory. Airbyte will stage data here
    // during sync and/or write small manifest/recovery files."
    //    )
    //    @get:JsonProperty("s3_staging_prefix")
    //    @get:JsonSchemaInject(json = """{"examples":["__staging/data_sync/test"]}""")
    //    val s3StagingPrefix: String?

    fun toObjectStoragePathConfiguration(): ObjectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = s3BucketPath,
            stagingPrefix = null,
            pathSuffixPattern = s3PathFormat,
            fileNamePattern = fileNamePattern,
            usesStagingDirectory = false
        )
}
