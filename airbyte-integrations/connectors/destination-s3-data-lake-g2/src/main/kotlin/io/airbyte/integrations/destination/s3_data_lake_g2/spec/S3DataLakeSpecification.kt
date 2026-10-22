/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake_g2.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.iceberg.parquet.CatalogType
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogSpecification
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogSpecifications
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Iceberg V2 Destination Specification")
class S3DataLakeSpecification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    S3BucketSpecification,
    IcebergCatalogSpecifications {

    @get:JsonSchemaTitle("AWS Access Key ID")
    @get:JsonPropertyDescription(
        "The AWS Access Key ID with permissions for S3 and Glue operations.",
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "always_show": true, "order":0}""")
    override val accessKeyId: String? = null

    @get:JsonSchemaTitle("AWS Secret Access Key")
    @get:JsonPropertyDescription(
        "The AWS Secret Access Key paired with the Access Key ID for AWS authentication.",
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "always_show": true, "order":1}""")
    override val secretAccessKey: String? = null

    @get:JsonSchemaTitle("S3 Bucket Name")
    @get:JsonPropertyDescription("The name of the S3 bucket that will host the Iceberg data.")
    @get:JsonSchemaInject(json = """{"always_show": true,"order":2}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"examples":["us-east-1"], "order":3}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"order":4}""") override val s3Endpoint: String? = null

    @get:JsonSchemaDescription(
        """The root location of the data warehouse used by the Iceberg catalog. Typically includes a bucket name and path within that bucket. For AWS Glue and Nessie, must include the storage protocol (such as "s3://" for Amazon S3).""",
    )
    @get:JsonSchemaInject(
        json =
            """
                {
                    "examples": ["s3://your-bucket/path/to/store/files/in"],
                    "always_show": true,
                    "order":5
                }
            """,
    )
    override val warehouseLocation: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":6}""")
    override val mainBranchName: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":7}""")
    override val catalogType: CatalogType = GlueCatalogSpecification(glueId = "", databaseName = "")

    @get:JsonSchemaTitle("Flush Batch Size (MB)")
    @get:JsonPropertyDescription(
        "The approximate size in megabytes of each batch of data written to Iceberg. " +
            "Smaller values flush more frequently, improving data freshness and reducing data loss on failure, " +
            "but will create more small files that require compaction. " +
            "Must be between 1 and 500 MB. Default is 200 MB.",
    )
    @get:JsonProperty("flush_batch_size_mb", required = false)
    @get:JsonSchemaInject(
        json = """{"examples":[200], "default": 200, "order": 8, "airbyte_hidden": true}""",
    )
    val flushBatchSizeMb: Long? = null

    @get:JsonSchemaTitle("Normalize Column Names")
    @get:JsonPropertyDescription(
        "Lowercases column names and replaces non-alphanumeric characters with underscores " +
            "before writing to Iceberg (e.g. \"Foo.Bar\" -> \"foo_bar\"). " +
            "Enable this when downstream query engines cannot handle mixed-case or " +
            "special-character column names. " +
            "IMPORTANT: toggling this on existing synced streams requires clearing the " +
            "stream data and running a full refresh.",
    )
    @get:JsonProperty("normalize_column_names", required = false)
    @get:JsonSchemaInject(json = """{"default": false, "order": 9}""")
    val normalizeColumnNames: Boolean? = null

    @get:JsonSchemaTitle("Iceberg Table Format Version")
    @get:JsonPropertyDescription(
        "The Iceberg table format version to create tables at. Version 2 is readable by every " +
            "engine that supports Iceberg. Version 3 adds deletion vectors, which some readers " +
            "(such as Databricks foreign Iceberg reads) require, but is not readable by Amazon " +
            "Athena today. Upgrading an existing table's format version is one-way; see " +
            "allow_non_reversible_upgrades.",
    )
    @get:JsonProperty("table_format_version", required = false)
    @get:JsonSchemaInject(json = """{"default":"v2","examples":["v2","v3"],"order":10}""")
    val tableFormatVersion: IcebergTableFormatVersion? = null

    @get:JsonSchemaTitle("Iceberg Delete File Type")
    @get:JsonPropertyDescription(
        "The delete-file encoding used by Dedupe streams. AUTOMATIC uses equality deletes on " +
            "format v2 tables and deletion vectors on format v3 tables, and may change in a " +
            "future version. Choose EQUALITY to always use equality deletes, POSITIONAL for " +
            "v2 readers that do not support equality-delete files, or DELETION_VECTOR for " +
            "v3 deletion vectors.",
    )
    @get:JsonProperty("iceberg_delete_file_type", required = false)
    @get:JsonSchemaInject(
        json =
            """{"default":"AUTOMATIC","examples":["AUTOMATIC","EQUALITY","POSITIONAL","DELETION_VECTOR"],"order":11}""",
    )
    val icebergDeleteFileType: IcebergDeleteFileType? = null

    @get:JsonSchemaTitle("Allow Non-Reversible Upgrades")
    @get:JsonPropertyDescription(
        "Controls whether an existing v2 table may be upgraded in place to format v3 when " +
            "table_format_version is v3. The upgrade is one-way and converts existing delete " +
            "files to deletion vectors. NO never upgrades; the table stays v2. YES upgrades in " +
            "place. WITH_TABLE_BACKUP registers a copy of the current table metadata as a " +
            "sibling v2 table before upgrading.",
    )
    @get:JsonProperty("allow_non_reversible_upgrades", required = false)
    @get:JsonSchemaInject(
        json = """{"default":"NO","examples":["NO","YES","WITH_TABLE_BACKUP"],"order":12}""",
    )
    val allowNonReversibleUpgrades: AllowNonReversibleUpgrades? = null

    @get:JsonSchemaTitle("Optimize Prior Iceberg Delete Files")
    @get:JsonPropertyDescription(
        "Experimental. Only applies when positional deletes are in use. When enabled, prior " +
            "positional delete files are consulted so that a position is deleted at most once. " +
            "Disabling it writes a delete for every physical copy of a row, which avoids reading " +
            "prior delete files at the cost of a larger delete-file population.",
    )
    @get:JsonProperty("optimize_prior_iceberg_delete_files", required = false)
    @get:JsonSchemaInject(json = """{"default":true,"order":13,"airbyte_hidden":true}""")
    val optimizePriorIcebergDeleteFiles: Boolean? = null

    @get:JsonSchemaTitle("Max Records Per Flush")
    @get:JsonPropertyDescription(
        "Experimental. The maximum number of records accumulated before a batch is written to " +
            "Iceberg. Flushes also trigger on the batch size in megabytes and on a staleness " +
            "deadline, so the first limit reached wins. Larger values write fewer, larger files " +
            "and reduce repeated work for Dedupe streams using positional deletes, at the cost of " +
            "holding more records in memory. Dedupe streams that use positional deletes " +
            "reject flushes containing more than 1,000,000 distinct primary keys.",
    )
    @get:JsonProperty("max_records_per_flush", required = false)
    @get:JsonSchemaInject(json = """{"default":10000000000,"order":14,"airbyte_hidden":true}""")
    val maxRecordsPerFlush: Long? = null
}

enum class IcebergDeleteFileType(@get:JsonValue val value: String) {
    AUTOMATIC("AUTOMATIC"),
    EQUALITY("EQUALITY"),
    POSITIONAL("POSITIONAL"),
    DELETION_VECTOR("DELETION_VECTOR"),
}

/** Whether an existing v2 table may be upgraded in place to format v3. */
enum class AllowNonReversibleUpgrades(@get:JsonValue val value: String) {
    NO("NO"),
    YES("YES"),
    WITH_TABLE_BACKUP("WITH_TABLE_BACKUP"),
}

/** The Iceberg table format version that Airbyte creates tables at. */
enum class IcebergTableFormatVersion(
    @get:JsonValue val specValue: String,
    val formatVersion: Int,
) {
    V2("v2", 2),
    V3("v3", 3),
}

@Singleton
class S3DataLakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
}
