/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Mix-in to provide S3 bucket configuration fields as properties.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 */
interface S3BucketSpecification {
    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription(
        "The name of the S3 bucket. Read more <a href=\"https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html\">here</a>."
    )
    @get:JsonProperty("s3_bucket_name")
    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"]}""")
    val s3BucketName: String

    @get:JsonSchemaTitle("S3 Bucket Region")
    @get:JsonPropertyDescription(
        "The region of the S3 bucket. See <a href=\"https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions\">here</a> for all region codes."
    )
    @get:JsonProperty("s3_bucket_region", defaultValue = "")
    @get:JsonSchemaInject(json = """{"examples":["us-east-1"]}""")
    val s3BucketRegion: String?

    @get:JsonSchemaTitle("S3 Endpoint")
    @get:JsonPropertyDescription(
        "Your S3 endpoint url. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/s3.html#:~:text=Service%20endpoints-,Amazon%20S3%20endpoints,-When%20you%20use\">here</a>"
    )
    @get:JsonProperty("s3_endpoint", defaultValue = "", required = false)
    @get:JsonSchemaInject(json = """{"examples":["http://localhost:9000"]}""")
    val s3Endpoint: String?

    fun toS3BucketConfiguration(): S3BucketConfiguration {
        return S3BucketConfiguration(s3BucketName, s3BucketRegion, s3Endpoint)
    }
}

data class S3BucketConfiguration(
    val s3BucketName: String,
    val s3BucketRegion: String?,
    val s3Endpoint: String?
)

interface S3BucketConfigurationProvider {
    val s3BucketConfiguration: S3BucketConfiguration
}
