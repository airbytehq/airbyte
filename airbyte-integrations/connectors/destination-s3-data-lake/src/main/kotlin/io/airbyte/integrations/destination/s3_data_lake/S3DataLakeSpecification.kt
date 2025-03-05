/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.iceberg.parquet.CatalogType
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogSpecification
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogSpecifications
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
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
        "The AWS Access Key ID with permissions for S3 and Glue operations."
    )
    @get:JsonSchemaInject(json = """{"airbyte_secret": true, "always_show": true, "order":0}""")
    override val accessKeyId: String? = null

    @get:JsonSchemaTitle("AWS Secret Access Key")
    @get:JsonPropertyDescription(
        "The AWS Secret Access Key paired with the Access Key ID for AWS authentication."
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
        """The root location of the data warehouse used by the Iceberg catalog. Typically includes a bucket name and path within that bucket. For AWS Glue and Nessie, must include the storage protocol (such as "s3://" for Amazon S3)."""
    )
    @get:JsonSchemaInject(
        json =
            """
                {
                    "examples": ["s3://your-bucket/path/to/store/files/in"],
                    "always_show": true,
                    "order":5
                }
            """
    )
    override val warehouseLocation: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":6}""")
    override val mainBranchName: String = ""

    @get:JsonSchemaInject(json = """{"always_show": true,"order":7}""")
    override val catalogType: CatalogType = GlueCatalogSpecification(glueId = "", databaseName = "")

    @get:JsonProperty("num_sockets") val numSockets: Int? = null

    @get:JsonProperty("num_part_loaders") val numPartLoaders: Int? = null

    @get:JsonProperty("input_serialization_format")
    val inputSerializationFormat: DestinationConfiguration.InputSerializationFormat? = null

    @get:JsonProperty("max_memory_ratio_reserved_for_parts")
    val maxMemoryRatioReservedForParts: Double? = null

    @get:JsonProperty("part_size_mb") val partSizeMb: Int? = null

    @get:JsonProperty("input_buffer_byte_size_per_socket")
    val inputBufferByteSizePerSocket: Long? = null

    @get:JsonProperty("socket_prefix") val socketPrefix: String? = null

    @get:JsonProperty("socket_wait_timeout_seconds") val socketWaitTimeoutSeconds: Int? = null

    @get:JsonProperty("dev_null_after_deserialization")
    val devNullAfterDeserialization: Boolean? = null

    @get:JsonProperty("skip_upload") val skipUpload: Boolean? = null

    @get:JsonProperty("use_garbage_part") val useGarbagePart: Boolean? = null

    @get:JsonProperty("num_part_formatters") val numInputPartitions: Int? = null

    @get:JsonProperty("skip_json_on_proto") val skipJsonOnProto: Boolean? = null

    @get:JsonProperty("disable_uuid") val disableUUID: Boolean? = null

    @get:JsonProperty("disable_mapper") val disableMapper: Boolean? = null

    @get:JsonProperty("use_coded_input_stream") val useCodedInputStream: Boolean? = null

    @get:JsonProperty("use_snappy") val useSnappy: Boolean? = null
}

@Singleton
class S3DataLakeSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP
        )
    override val supportsIncremental = true
}
