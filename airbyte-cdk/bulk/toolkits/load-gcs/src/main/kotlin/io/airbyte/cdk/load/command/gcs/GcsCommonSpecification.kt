/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/** Represents basic GCS options. You may also want to extend [GcsRegionSpecification]. */
interface GcsCommonSpecification {
    @get:JsonSchemaTitle("GCS Bucket Name")
    @get:JsonPropertyDescription(
        """The name of the GCS bucket. Read more <a href="https://cloud.google.com/storage/docs/naming-buckets">here</a>."""
    )
    @get:JsonProperty("gcs_bucket_name")
    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"], "order": 1}""")
    val gcsBucketName: String

    @get:JsonSchemaTitle("GCS Bucket Path")
    @get:JsonPropertyDescription("Directory under the GCS bucket where data will be written.")
    @get:JsonProperty("gcs_bucket_path")
    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"], "order": 2}""")
    val path: String

    @get:JsonSchemaTitle("Credential")
    // we have to put this description here, or it doesn't show up in the UI
    @get:JsonPropertyDescription(
        """An HMAC key is a type of credential and can be associated with a service account or a user account in Cloud Storage. Read more <a href="https://cloud.google.com/storage/docs/authentication/hmackeys">here</a>."""
    )
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val credential: GcsAuthSpecification
}
