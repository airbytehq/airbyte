/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

/**
 * The object which is mapped to the BigQuery source configuration JSON.
 *
 * Property names, titles and descriptions deliberately mirror the legacy `source-bigquery`
 * `spec.json` so that existing configurations keep deserializing. Use [BigQuerySourceConfiguration]
 * instead wherever possible.
 */
@JsonSchemaTitle("BigQuery Source Spec")
@JsonPropertyOrder(value = ["project_id", "dataset_id", "credentials_json"])
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class BigQuerySourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("project_id")
    @JsonSchemaTitle("Project ID")
    @JsonSchemaDescription(
        "The GCP project ID for the project containing the target BigQuery dataset."
    )
    lateinit var projectId: String

    /** Null when the (required) `project_id` property is absent from the config JSON. */
    fun projectIdOrNull(): String? = if (this::projectId.isInitialized) projectId else null

    @JsonProperty("dataset_id")
    @JsonSchemaTitle("Default Dataset ID")
    @JsonSchemaDescription(
        "The dataset ID to search for tables and views. If you are only loading data from one dataset, setting this option could result in much faster schema discovery."
    )
    var datasetId: String? = null

    @JsonProperty("credentials_json")
    @JsonSchemaTitle("Credentials JSON")
    @JsonSchemaDescription(
        "The contents of your Service Account Key JSON file. See the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery#setup-the-bigquery-source-in-airbyte\">docs</a> for more information on how to obtain this key."
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    lateinit var credentialsJson: String

    /** Null when the (required) `credentials_json` property is absent from the config JSON. */
    fun credentialsJsonOrNull(): String? =
        if (this::credentialsJson.isInitialized) credentialsJson else null
}
