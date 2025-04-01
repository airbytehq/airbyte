/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.s3

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface GcsBucketSpecification {
    @get:JsonSchemaTitle("GCS Bucket Name")
    @get:JsonPropertyDescription(
        """The name of the GCS bucket. Read more <a href=\"https://cloud.google.com/storage/docs/naming-buckets\">here</a>."""
    )
    @get:JsonProperty("gcs_bucket_name")
    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"]}""")
    val gcsBucketName: String

    fun toGcsBucketConfiguration(): GcsBucketConfiguration {
        return GcsBucketConfiguration(gcsBucketName)
    }
}

data class GcsBucketConfiguration(val gcsBucketName: String)

interface S3BucketConfigurationProvider {
    val s3BucketConfiguration: GcsBucketConfiguration
}
