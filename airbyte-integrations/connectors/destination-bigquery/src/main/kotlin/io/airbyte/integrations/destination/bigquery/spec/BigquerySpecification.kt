/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.fasterxml.jackson.core.JsonParser
import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.databind.DeserializationContext
import com.fasterxml.jackson.databind.JsonDeserializer
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.annotation.JsonDeserialize
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.gcs.GcsAuthSpecification
import io.airbyte.cdk.load.command.gcs.GcsCommonSpecification
import io.airbyte.cdk.load.command.gcs.GcsHmacKeySpecification
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton
import java.io.IOException

@Singleton
class BigquerySpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Project ID")
    @get:JsonPropertyDescription(
        """The GCP project ID for the project containing the target BigQuery dataset. Read more <a href="https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects">here</a>.""",
    )
    @get:JsonProperty("project_id")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 0}""")
    val projectId: String = ""

    @get:JsonSchemaTitle("Dataset Location")
    @get:JsonPropertyDescription(
        """The location of the dataset. Warning: Changes made after creation will not be applied. Read more <a href="https://cloud.google.com/bigquery/docs/locations">here</a>.""",
    )
    @get:JsonProperty("dataset_location")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 1}""")
    val datasetLocation: BigqueryRegion = BigqueryRegion.US_EAST1

    @get:JsonSchemaTitle("Default Dataset ID")
    @get:JsonPropertyDescription(
        """The default BigQuery Dataset ID that tables are replicated to if the source does not specify a namespace. Read more <a href="https://cloud.google.com/bigquery/docs/datasets#create-dataset">here</a>.""",
    )
    @get:JsonProperty("dataset_id")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 2}""")
    val datasetId: String = ""

    @get:JsonSchemaTitle("Loading Method")
    @get:JsonPropertyDescription("""The way data will be uploaded to BigQuery.""")
    @get:JsonProperty("loading_method")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 3, "display_type": "radio"}""")
    val loadingMethod: LoadingMethodSpecification? = BatchedStandardInsertSpecification()

    // older versions of the connector represented this field as an actual JSON object,
    // so we need to use the RawJsonDeserializer.
    @get:JsonDeserialize(using = RawJsonDeserializer::class)
    @get:JsonSchemaTitle("Service Account Key JSON (Required for cloud, optional for open-source)")
    @get:JsonPropertyDescription(
        """The contents of the JSON service account key. Check out the <a href="https://docs.airbyte.com/integrations/destinations/bigquery#service-account-key">docs</a> if you need help generating this key. Default credentials will be used if this field is left empty.""",
    )
    @get:JsonProperty("credentials_json")
    @get:JsonSchemaInject(
        json =
            """{"group": "connection", "order": 4, "airbyte_secret": true, "always_show": true}""",
    )
    val credentialsJson: String? = null

    @get:JsonSchemaTitle("CDC deletion mode")
    @get:JsonPropertyDescription(
        """Whether to execute CDC deletions as hard deletes (i.e. propagate source deletions to the destination), or soft deletes (i.e. leave a tombstone record in the destination). Defaults to hard deletes.""",
    )
    // default hard delete for backwards compatibility
    @get:JsonProperty("cdc_deletion_mode", defaultValue = "Hard delete")
    @get:JsonSchemaInject(
        json = """{"group": "sync_behavior", "order": 5, "always_show": true}""",
    )
    val cdcDeletionMode: CdcDeletionMode? = null

    @get:JsonSchemaTitle(
        """Legacy raw tables""",
    )
    @get:JsonPropertyDescription(
        """Write the legacy "raw tables" format, to enable backwards compatibility with older versions of this connector.""",
    )
    // for compatibility with existing actor configs, we keep the old property name.
    @get:JsonProperty("disable_type_dedupe")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 7, "default": false}""")
    val legacyRawTablesOnly: Boolean? = null

    @get:JsonSchemaTitle("Airbyte Internal Table Dataset Name")
    @get:JsonPropertyDescription(
        """Airbyte will use this dataset for various internal tables. In legacy raw tables mode, the raw tables will be stored in this dataset. Defaults to "airbyte_internal".""",
    )
    // for backwards compatibility, the JSON property is still called raw_data_dataset.
    @get:JsonProperty("raw_data_dataset")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 8}""")
    val internalTableDataset: String? = null

    @get:JsonSchemaTitle("Default Partitioning Field")
    @get:JsonPropertyDescription("Default field to use for partitioning (e.g. _airbyte_extracted_at)")
    @get:JsonProperty("default_partitioning_field")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 10}""")
    val defaultPartitioningField: String? = null

    @get:JsonSchemaTitle("Default Clustering Field")
    @get:JsonPropertyDescription("Default field to use for clustering (e.g. _airbyte_extracted_at)")
    @get:JsonProperty("default_clustering_field")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 11}""")
    val defaultClusteringField: String? = null

    @get:JsonSchemaTitle("Default Table Suffix")
    @get:JsonPropertyDescription("Default suffix to append to table names")
    @get:JsonProperty("default_table_suffix")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 12}""")
    val defaultTableSuffix: String? = null

    @get:JsonSchemaTitle("Stream Configuration")
    @get:JsonPropertyDescription(
        """Per-stream configuration overrides.""",
    )
    @get:JsonProperty("streams")
    @get:JsonSchemaInject(json = """{"group": "advanced", "order": 13}""")
    val streams: List<SingleStreamConfiguration>? = null
}

/**
 * Per-stream configuration for custom partitioning, clustering, and table naming.
 */
data class SingleStreamConfiguration(
    @get:JsonSchemaTitle("Stream Name")
    @get:JsonPropertyDescription("Name of the stream (or namespace.stream_name)")
    @JsonProperty("name")
    val name: String = "",

    @get:JsonSchemaTitle("Partitioning Field")
    @JsonProperty("partitioning_field")
    val partitioningField: String? = null,

    @get:JsonSchemaTitle("Clustering Field")
    @JsonProperty("clustering_field")
    val clusteringField: String? = null,

    @get:JsonSchemaTitle("Table Suffix")
    @JsonProperty("table_suffix")
    val tableSuffix: String? = null,

    @get:JsonSchemaTitle("Target Dataset")
    @JsonProperty("dataset")
    val dataset: String? = null,
)

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "method",
)
@JsonSubTypes(
    JsonSubTypes.Type(value = BatchedStandardInsertSpecification::class, name = "Standard"),
    JsonSubTypes.Type(value = GcsStagingSpecification::class, name = "GCS Staging"),
    JsonSubTypes.Type(value = StorageWriteApiSpecification::class, name = "Storage Write API"),
)
sealed class LoadingMethodSpecification(@JsonProperty("method") val method: LoadingMethod) {
    enum class LoadingMethod(@get:JsonValue val typeName: String) {
        BATCHED_STANDARD_INSERT("Standard"),
        GCS("GCS Staging"),
        STORAGE_WRITE_API("Storage Write API"),
    }
}

@JsonSchemaTitle("Batched Standard Inserts")
@JsonSchemaDescription(
    "Direct loading using batched SQL INSERT statements. This method uses the BigQuery driver to convert large INSERT statements into file uploads automatically.",
)
class BatchedStandardInsertSpecification :
    LoadingMethodSpecification(LoadingMethod.BATCHED_STANDARD_INSERT)

@JsonSchemaTitle("GCS Staging")
@JsonSchemaDescription(
    "Writes large batches of records to a file, uploads the file to GCS, then uses COPY INTO to load your data into BigQuery.",
)
class GcsStagingSpecification :
    GcsCommonSpecification, LoadingMethodSpecification(LoadingMethod.GCS) {
    @get:JsonSchemaTitle("GCS Tmp Files Post-Processing")
    @get:JsonPropertyDescription(
        """This upload method is supposed to temporary store records in GCS bucket. By this select you can chose if these records should be removed from GCS when migration has finished. The default "Delete all tmp files from GCS" value is used if not set explicitly.""",
    )
    // yes, this is mixed underscore+hyphen.
    @get:JsonProperty("keep_files_in_gcs-bucket", defaultValue = "Delete all tmp files from GCS")
    @get:JsonSchemaInject(json = """{"order": 3}""")
    val filePostProcessing: GcsFilePostProcessing? = null
    override val gcsBucketName: String = ""
    override val path: String = ""
    override val credential: GcsAuthSpecification =
        GcsHmacKeySpecification(accessKeyId = "", secretAccessKey = "")
}

@JsonSchemaTitle("Storage Write API")
@JsonSchemaDescription(
    "Uses BigQuery Storage Write API for direct streaming writes. This method bypasses partition modification quota limits and provides better throughput for high-frequency syncs.",
)
class StorageWriteApiSpecification :
    LoadingMethodSpecification(LoadingMethod.STORAGE_WRITE_API) {
    @get:JsonSchemaTitle("Max Inflight Requests")
    @get:JsonPropertyDescription(
        """Maximum number of concurrent append requests. Higher values increase throughput but consume more memory. Default: 1000""",
    )
    @get:JsonProperty("max_inflight_requests")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val maxInflightRequests: Int? = null

    @get:JsonSchemaTitle("Max Inflight Bytes")
    @get:JsonPropertyDescription(
        """Maximum bytes buffered in memory for inflight requests. Default: 10485760 (10MB)""",
    )
    @get:JsonProperty("max_inflight_bytes")
    @get:JsonSchemaInject(json = """{"order": 1}""")
    val maxInflightBytes: Long? = null

    @get:JsonSchemaTitle("Batch Size")
    @get:JsonPropertyDescription(
        """Number of records to batch before appending to BigQuery. Higher values reduce API calls but increase latency. Default: 1000""",
    )
    @get:JsonProperty("batch_size")
    @get:JsonSchemaInject(json = """{"order": 2}""")
    val batchSize: Int? = null
}

// bigquery supports a subset of GCS regions.
// See https://cloud.google.com/bigquery/docs/locations#supported_locations
enum class BigqueryRegion(@get:JsonValue val region: String, val gcsRegion: GcsRegion) {
    EU("EU", GcsRegion.EU),
    US("US", GcsRegion.US),
    AFRICA_SOUTH1("africa-south1", GcsRegion.AFRICA_SOUTH1),
    ASIA_EAST1("asia-east1", GcsRegion.ASIA_EAST1),
    ASIA_EAST2("asia-east2", GcsRegion.ASIA_EAST2),
    ASIA_NORTHEAST1("asia-northeast1", GcsRegion.ASIA_NORTHEAST1),
    ASIA_NORTHEAST2("asia-northeast2", GcsRegion.ASIA_NORTHEAST2),
    ASIA_NORTHEAST3("asia-northeast3", GcsRegion.ASIA_NORTHEAST3),
    ASIA_SOUTH1("asia-south1", GcsRegion.ASIA_SOUTH1),
    ASIA_SOUTH2("asia-south2", GcsRegion.ASIA_SOUTH2),
    ASIA_SOUTHEAST1("asia-southeast1", GcsRegion.ASIA_SOUTHEAST1),
    ASIA_SOUTHEAST2("asia-southeast2", GcsRegion.ASIA_SOUTHEAST2),
    AUSTRALIA_SOUTHEAST1("australia-southeast1", GcsRegion.AUSTRALIA_SOUTHEAST1),
    AUSTRALIA_SOUTHEAST2("australia-southeast2", GcsRegion.AUSTRALIA_SOUTHEAST2),
    EUROPE_CENTRAL2("europe-central2", GcsRegion.EUROPE_CENTRAL2),
    EUROPE_NORTH1("europe-north1", GcsRegion.EUROPE_NORTH1),
    EUROPE_NORTH2("europe-north2", GcsRegion.EUROPE_NORTH2),
    EUROPE_SOUTHWEST1("europe-southwest1", GcsRegion.EUROPE_SOUTHWEST1),
    EUROPE_WEST1("europe-west1", GcsRegion.EUROPE_WEST1),
    EUROPE_WEST2("europe-west2", GcsRegion.EUROPE_WEST2),
    EUROPE_WEST3("europe-west3", GcsRegion.EUROPE_WEST3),
    EUROPE_WEST4("europe-west4", GcsRegion.EUROPE_WEST4),
    EUROPE_WEST6("europe-west6", GcsRegion.EUROPE_WEST6),
    EUROPE_WEST8("europe-west8", GcsRegion.EUROPE_WEST8),
    EUROPE_WEST9("europe-west9", GcsRegion.EUROPE_WEST9),
    EUROPE_WEST10("europe-west10", GcsRegion.EUROPE_WEST10),
    EUROPE_WEST12("europe-west12", GcsRegion.EUROPE_WEST12),
    ME_CENTRAL1("me-central1", GcsRegion.ME_CENTRAL1),
    ME_CENTRAL2("me-central2", GcsRegion.ME_CENTRAL2),
    ME_WEST1("me-west1", GcsRegion.ME_WEST1),
    NORTHAMERICA_NORTHEAST1("northamerica-northeast1", GcsRegion.NORTHAMERICA_NORTHEAST1),
    NORTHAMERICA_NORTHEAST2("northamerica-northeast2", GcsRegion.NORTHAMERICA_NORTHEAST2),
    NORTHAMERICA_SOUTH1("northamerica-south1", GcsRegion.NORTHAMERICA_SOUTH1),
    SOUTHAMERICA_EAST1("southamerica-east1", GcsRegion.SOUTHAMERICA_EAST1),
    SOUTHAMERICA_WEST1("southamerica-west1", GcsRegion.SOUTHAMERICA_WEST1),
    US_CENTRAL1("us-central1", GcsRegion.US_CENTRAL1),
    US_EAST1("us-east1", GcsRegion.US_EAST1),
    US_EAST4("us-east4", GcsRegion.US_EAST4),
    US_EAST5("us-east5", GcsRegion.US_EAST5),
    US_SOUTH1("us-south1", GcsRegion.US_SOUTH1),
    US_WEST1("us-west1", GcsRegion.US_WEST1),
    US_WEST2("us-west2", GcsRegion.US_WEST2),
    US_WEST3("us-west3", GcsRegion.US_WEST3),
    US_WEST4("us-west4", GcsRegion.US_WEST4),
}

enum class GcsFilePostProcessing(@get:JsonValue val postProcesing: String) {
    DELETE("Delete all tmp files from GCS"),
    KEEP("Keep all tmp files in GCS"),
}

enum class TransformationPriority(@get:JsonValue val transformationPriority: String) {
    INTERACTIVE("interactive"),
    BATCH("batch")
}

enum class CdcDeletionMode(@get:JsonValue val cdcDeletionMode: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}

@Singleton
class BigquerySpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("sync_behavior", "Sync Behavior"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}

/**
 * A custom JSON deserializer, which can write any JSON value into a String field. In particular, it
 * passes String values through unchanged, but serializes all other values.
 *
 * If you don't do this, then Jackson will choke on object values.
 */
class RawJsonDeserializer : JsonDeserializer<String?>() {
    @Throws(IOException::class, JsonProcessingException::class)
    override fun deserialize(jp: JsonParser, ctxt: DeserializationContext?): String {
        val node: JsonNode = Jsons.readTree(jp)
        if (node.isTextual) {
            return node.asText()
        }
        return Jsons.writeValueAsString(node)
    }
}
