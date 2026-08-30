/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("GCS Data Lake Destination Specification")
@JsonSchemaDescription("Configuration for GCS Data Lake destination using Apache Iceberg format")
class GcsDataLakeSpecification : ConfigurationSpecification() {

    @get:JsonSchemaTitle("GCS Bucket Name")
    @get:JsonPropertyDescription("The name of the GCS bucket that will host the Iceberg data.")
    @get:JsonProperty("gcs_bucket_name")
    @get:JsonSchemaInject(json = """{"always_show": true, "order": 0}""")
    val gcsBucketName: String = ""

    @get:JsonSchemaTitle("Service Account JSON")
    @get:JsonPropertyDescription(
        """The contents of the JSON service account key file. See the <a href="https://cloud.google.com/iam/docs/creating-managing-service-account-keys">Google Cloud documentation</a> for more information on how to obtain this."""
    )
    @get:JsonProperty("service_account_json")
    @get:JsonSchemaInject(
        json =
            """
            {
                "airbyte_secret": true,
                "always_show": true,
                "multiline": true,
                "order": 1
            }
        """
    )
    val serviceAccountJson: String = ""

    @get:JsonSchemaTitle("GCP Project ID")
    @get:JsonPropertyDescription(
        "The GCP project ID where resources are located. If not specified, it will be extracted from the service account credentials."
    )
    @get:JsonProperty("gcp_project_id")
    @get:JsonSchemaInject(json = """{"order": 2}""")
    val gcpProjectId: String? = null

    @get:JsonSchemaTitle("GCP Location")
    @get:JsonPropertyDescription(
        """The GCP location (region) for BigLake metastore resources. For example: "us-central1" or "us". See <a href="https://cloud.google.com/biglake/docs/locations">BigLake locations</a> for available regions."""
    )
    @get:JsonProperty("gcp_location")
    @get:JsonSchemaInject(
        json =
            """
            {
                "examples": ["us", "us-central1", "eu"],
                "always_show": true,
                "order": 3
            }
        """
    )
    val gcpLocation: String = "us"

    @get:JsonSchemaTitle("Warehouse Location")
    @get:JsonSchemaDescription(
        """The root location of the data warehouse used by the Iceberg catalog. Must include the storage protocol "gs://" for Google Cloud Storage. For example: "gs://your-bucket/path/to/warehouse/"""
    )
    @get:JsonProperty("warehouse_location")
    @get:JsonSchemaInject(
        json =
            """
            {
                "examples": ["gs://your-bucket/path/to/warehouse"],
                "always_show": true,
                "order": 4
            }
        """
    )
    val warehouseLocation: String = ""

    @get:JsonSchemaTitle("Main Branch Name")
    @get:JsonPropertyDescription(
        """The primary or default branch name in the catalog. Most query engines will use "main" by default. See <a href="https://iceberg.apache.org/docs/latest/branching/">Iceberg documentation</a> for more information."""
    )
    @get:JsonProperty("main_branch_name")
    @get:JsonSchemaInject(json = """{"order": 5}""")
    val mainBranchName: String = "main"

    @get:JsonSchemaTitle("Default Namespace")
    @get:JsonPropertyDescription(
        """The default namespace to use for tables. This will ONLY be used if the `Destination Namespace` setting is set to `Destination-defined` or `Source-defined`"""
    )
    @get:JsonProperty("namespace")
    @get:JsonSchemaInject(json = """{"examples": ["default", "airbyte_data"], "order": 6}""")
    val namespace: String = "default"

    @get:JsonSchemaTitle("Catalog Type")
    @get:JsonPropertyDescription("Specifies the type of Iceberg catalog (BigLake or Polaris).")
    @get:JsonProperty("catalog_type")
    @get:JsonSchemaInject(json = """{"always_show": true, "order": 7}""")
    val catalogType: GcsCatalogType = BigLakeCatalogSpec(catalogName = "integration-test-biglake")

    @get:JsonSchemaTitle("GCS Endpoint (Optional)")
    @get:JsonPropertyDescription(
        "Optional custom GCS endpoint URL. Use this for testing with local GCS emulators."
    )
    @get:JsonProperty("gcs_endpoint")
    @get:JsonSchemaInject(json = """{"order": 8}""")
    val gcsEndpoint: String? = null

    @get:JsonSchemaTitle("Merge-on-Read Delete Encoding")
    @get:JsonPropertyDescription(
        "The delete-file encoding used by Dedupe streams. AUTOMATIC currently uses equality deletes " +
            "but may change in a future version. Choose EQUALITY to always use equality deletes, or " +
            "POSITIONAL for readers that do not support equality-delete files."
    )
    @get:JsonProperty("merge_on_read_delete_encoding", required = false)
    @get:JsonSchemaInject(
        json =
            """{"default":"AUTOMATIC","examples":["AUTOMATIC","EQUALITY","POSITIONAL"],"order":9}"""
    )
    val mergeOnReadDeleteEncoding: MergeOnReadDeleteEncoding? = null

    @get:JsonSchemaTitle("Suppress Already-Deleted Positions")
    @get:JsonPropertyDescription(
        "Experimental. Only applies when positional deletes are in use. When enabled, prior " +
            "positional delete files are consulted so that a position is deleted at most once. " +
            "Disabling it writes a delete for every physical copy of a row, which avoids reading " +
            "prior delete files at the cost of a larger delete-file population."
    )
    @get:JsonProperty("suppress_deleted_positions", required = false)
    @get:JsonSchemaInject(json = """{"default":true,"order":10,"airbyte_hidden":true}""")
    val suppressDeletedPositions: Boolean? = null

    @get:JsonSchemaTitle("Index Positional Deletes")
    @get:JsonPropertyDescription(
        "Experimental. Only applies when positional deletes are in use with suppression enabled. " +
            "Publishes a deletion-vector index alongside the table as Iceberg statistics so later " +
            "flushes can skip reading prior delete files. The index is an accelerator only; " +
            "delete files remain the source of truth and readers are unaffected."
    )
    @get:JsonProperty("index_positional_deletes", required = false)
    @get:JsonSchemaInject(json = """{"default":false,"order":11,"airbyte_hidden":true}""")
    val indexPositionalDeletes: Boolean? = null

    @get:JsonSchemaTitle("Max Records Per Flush")
    @get:JsonPropertyDescription(
        "Experimental. The maximum number of records accumulated before a batch is written to " +
            "Iceberg. Flushes also trigger on an estimated batch size in bytes and on a staleness " +
            "deadline, so the first limit reached wins. Larger values write fewer, larger files " +
            "and reduce repeated work for Dedupe streams using positional deletes, at the cost of " +
            "holding more records in memory."
    )
    @get:JsonProperty("max_records_per_flush", required = false)
    @get:JsonSchemaInject(json = """{"default":10000000000,"order":12,"airbyte_hidden":true}""")
    val maxRecordsPerFlush: Long? = null

    fun toGcsCatalogConfiguration(): GcsCatalogConfiguration {
        val catalogConfig =
            when (catalogType) {
                is BigLakeCatalogSpec -> {
                    val spec = catalogType as BigLakeCatalogSpec
                    BigLakeCatalogConfiguration(
                        catalogName = spec.catalogName,
                        gcpLocation = gcpLocation
                    )
                }
                is PolarisCatalogSpec -> {
                    val spec = catalogType as PolarisCatalogSpec
                    PolarisCatalogConfiguration(
                        serverUri = spec.serverUri,
                        catalogName = spec.catalogName,
                        clientId = spec.clientId,
                        clientSecret = spec.clientSecret,
                    )
                }
            }

        return GcsCatalogConfiguration(
            warehouseLocation = warehouseLocation,
            mainBranchName = mainBranchName,
            catalogConfiguration = catalogConfig
        )
    }
}

enum class MergeOnReadDeleteEncoding(@get:JsonValue val value: String) {
    AUTOMATIC("AUTOMATIC"),
    EQUALITY("EQUALITY"),
    POSITIONAL("POSITIONAL"),
}

@Singleton
class GcsDataLakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP
        )
    override val supportsIncremental = true
}
