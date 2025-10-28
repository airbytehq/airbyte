/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.iceberg.parquet.CatalogType
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogSpecifications
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("GCS Data Lake Destination Specification")
@JsonSchemaDescription("Configuration for GCS Data Lake destination using Apache Iceberg format")
class GcsDataLakeSpecification :
    ConfigurationSpecification(),
    IcebergCatalogSpecifications {

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
        json = """
            {
                "airbyte_secret": true,
                "always_show": true,
                "multiline": true,
                "order": 1
            }
        """
    )
    val serviceAccountJson: String = ""

    @get:JsonSchemaTitle("GCS Endpoint (Optional)")
    @get:JsonPropertyDescription(
        "Optional custom GCS endpoint URL. Use this for testing with local GCS emulators."
    )
    @get:JsonProperty("gcs_endpoint")
    @get:JsonSchemaInject(json = """{"order": 2}""")
    val gcsEndpoint: String? = null

    @get:JsonSchemaTitle("Warehouse Location")
    @get:JsonSchemaDescription(
        """The root location of the data warehouse used by the Iceberg catalog. Must include the storage protocol "gs://" for Google Cloud Storage. For example: "gs://your-bucket/path/to/warehouse/"""
    )
    @get:JsonProperty("warehouse_location")
    @get:JsonSchemaInject(
        json = """
            {
                "examples": ["gs://your-bucket/path/to/store/files/in"],
                "always_show": true,
                "order": 3
            }
        """
    )
    override val warehouseLocation: String = ""

    @get:JsonSchemaTitle("Main Branch Name")
    @get:JsonPropertyDescription(
        """The primary or default branch name in the catalog. Most query engines will use "main" by default. See <a href="https://iceberg.apache.org/docs/latest/branching/">Iceberg documentation</a> for more information."""
    )
    @get:JsonProperty("main_branch_name")
    @get:JsonSchemaInject(json = """{"always_show": true, "order": 4}""")
    override val mainBranchName: String = "main"

    @get:JsonSchemaTitle("Catalog Type")
    @get:JsonPropertyDescription(
        "Specifies the type of Iceberg catalog (NESSIE, REST, or POLARIS) and its associated configuration."
    )
    @get:JsonProperty("catalog_type")
    @get:JsonSchemaInject(json = """{"always_show": true, "order": 5}""")
    override val catalogType: CatalogType = NessieCatalogSpecification(
        serverUri = "",
        accessToken = null,
        namespace = ""
    )
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
