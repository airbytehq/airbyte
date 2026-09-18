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
 * The property names of the legacy `source-bigquery` connector (`project_id`, `dataset_id`,
 * `credentials_json`) and its `required` list are kept so that saved configurations keep
 * deserializing. Titles, descriptions and the `connection`/`advanced` groups follow
 * `destination-bigquery` (minus its destination-only properties); `max_db_connections` is the
 * performance property shared by the other Bulk CDK sources. Use [BigQuerySourceConfiguration]
 * instead wherever possible.
 */
@JsonSchemaTitle("BigQuery Source Spec")
@JsonSchemaInject(
    json =
        """{"groups":[{"id":"connection","title":"Connection"},{"id":"advanced","title":"Advanced"}]}"""
)
@JsonPropertyOrder(
    value =
        [
            "project_id",
            "dataset_id",
            "credentials_json",
            "job_project_id",
            "max_db_connections",
            "use_storage_read_api",
        ]
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class BigQuerySourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("project_id")
    @JsonSchemaTitle("Project ID")
    @JsonSchemaDescription(
        "The GCP project ID for the project containing the BigQuery datasets to read from. Read more <a href=\"https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects\">here</a>."
    )
    @JsonSchemaInject(json = """{"group":"connection","order":0}""")
    lateinit var projectId: String

    /** Null when the (required) `project_id` property is absent from the config JSON. */
    fun projectIdOrNull(): String? = if (this::projectId.isInitialized) projectId else null

    @JsonProperty("dataset_id")
    @JsonSchemaTitle("Dataset ID")
    @JsonSchemaDescription(
        "The BigQuery dataset to read tables and views from. Leave empty to discover every dataset of the project; setting it makes schema discovery much faster on projects with many datasets. Read more <a href=\"https://cloud.google.com/bigquery/docs/datasets-intro\">here</a>."
    )
    @JsonSchemaInject(json = """{"group":"connection","order":1}""")
    var datasetId: String? = null

    @JsonProperty("credentials_json")
    @JsonSchemaTitle("Service Account Key JSON")
    @JsonSchemaDescription(
        "The contents of the JSON service account key. Check out the <a href=\"https://docs.airbyte.com/integrations/sources/bigquery-v2#service-account-key\">docs</a> if you need help generating this key."
    )
    @JsonSchemaInject(
        json = """{"group":"connection","order":2,"airbyte_secret":true,"always_show":true}"""
    )
    lateinit var credentialsJson: String

    /** Null when the (required) `credentials_json` property is absent from the config JSON. */
    fun credentialsJsonOrNull(): String? =
        if (this::credentialsJson.isInitialized) credentialsJson else null

    @JsonProperty("job_project_id")
    @JsonSchemaTitle("Job Execution Project ID")
    @JsonSchemaDescription(
        "Optional. The GCP project ID where BigQuery query jobs are run. When set, the queries of a sync run against this project's quota and billing instead of the data project's. This isolates the concurrent query quota between workloads (e.g. data extraction vs. analytics) and allows reading from a project in which the service account only has data access. The service account must have the BigQuery Job User role on this project. If not set, jobs run in the data project (Project ID above)."
    )
    @JsonSchemaInject(json = """{"group":"advanced","order":3}""")
    var jobProjectId: String? = null

    @JsonProperty("max_db_connections")
    @JsonSchemaTitle("Max Concurrent Queries to Database")
    @JsonSchemaDescription(
        "Maximum number of concurrent queries to the database. Leave empty to let Airbyte optimize performance."
    )
    @JsonSchemaInject(json = """{"group":"advanced","order":4,"always_show":true,"minimum":1}""")
    var maxDbConnections: Int? = null

    @JsonProperty("use_storage_read_api")
    @JsonSchemaTitle("Use the BigQuery Storage Read API")
    @JsonSchemaDescription(
        "Read query results through the high-throughput BigQuery Storage Read API instead of the REST API. This is many times faster for large tables. It requires the service account to have the BigQuery Read Session User role (the bigquery.readsessions.create permission), and Storage Read API usage is billed separately from query bytes. Read more <a href=\"https://cloud.google.com/bigquery/docs/reference/storage\">here</a>."
    )
    @JsonSchemaInject(json = """{"group":"advanced","order":5}""")
    var useStorageReadApi: Boolean? = null
}
