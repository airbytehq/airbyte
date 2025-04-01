/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.gcs

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface GcsPathSpecification {
    @get:JsonSchemaTitle("GCS Bucket Path")
    @get:JsonPropertyDescription("Directory under the GCS bucket where data will be written.")
    @get:JsonProperty("gcs_bucket_path")
    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"]}""")
    val path: String
}

data class GcsPathConfiguration(val path: String)

interface GcsPathConfigurationProvider {
    val gcsPathConfiguration: GcsPathConfiguration
}
