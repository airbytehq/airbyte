/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

enum class S3BucketRegion {
    `af-south-1`,
    `ap-east-1`,
    `ap-northeast-1`,
    `ap-northeast-2`,
    `ap-northeast-3`,
    `ap-south-1`,
    `ap-south-2`,
    `ap-southeast-1`,
    `ap-southeast-2`,
    `ap-southeast-3`,
    `ap-southeast-4`,
    `ca-central-1`,
    `ca-west-1`,
    `cn-north-1`,
    `cn-northwest-1`,
    `eu-central-1`,
    `eu-central-2`,
    `eu-north-1`,
    `eu-south-1`,
    `eu-south-2`,
    `eu-west-1`,
    `eu-west-2`,
    `eu-west-3`,
    `il-central-1`,
    `me-central-1`,
    `me-south-1`,
    `sa-east-1`,
    `us-east-1`,
    `us-east-2`,
    `us-gov-east-1`,
    `us-gov-west-1`,
    `us-west-1`,
    `us-west-2`
}

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
    val s3BucketRegion: S3BucketRegion

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
    val s3BucketRegion: S3BucketRegion,
    val s3Endpoint: String?
)

interface S3BucketConfigurationProvider {
    val s3BucketConfiguration: S3BucketConfiguration
}
