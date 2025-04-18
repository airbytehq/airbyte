/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import com.fasterxml.jackson.annotation.JsonProperty
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeySpecification
import io.airbyte.cdk.load.command.aws.AWSArnRoleSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedJsonFormatSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.s3.S3BucketRegion
import io.airbyte.cdk.load.command.s3.S3BucketSpecification
import io.airbyte.cdk.load.command.s3.S3PathSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("S3 V2 Destination Spec")
@JsonSchemaInject()
class S3V2Specification :
    ConfigurationSpecification(),
    AWSAccessKeySpecification,
    AWSArnRoleSpecification,
    S3BucketSpecification,
    S3PathSpecification,
    DeprecatedObjectStorageFormatSpecificationProvider {

    @get:JsonSchemaInject(
        json =
            """{"examples":["A012345678910EXAMPLE"],"airbyte_secret": true,"always_show": true,"order":0}"""
    )
    override val accessKeyId: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"],"airbyte_secret": true,"always_show": true,"order":1}"""
    )
    override val secretAccessKey: String? = null

    @get:JsonSchemaInject(
        json =
            """{"examples":["arn:aws:iam::123456789:role/ExternalIdIsYourWorkspaceId"],"order":2}"""
    )
    override val roleArn: String? = null

    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":3}""")
    override val s3BucketName: String = ""

    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"],"order":4}""")
    override val s3BucketPath: String = ""

    @get:JsonSchemaInject(json = """{"examples":["us-east-1"],"order":5,"default":""}""")
    override val s3BucketRegion: S3BucketRegion = S3BucketRegion.NO_REGION

    @get:JsonSchemaInject(json = """{"order":6}""")
    override val format: DeprecatedObjectStorageFormatSpecification =
        DeprecatedJsonFormatSpecification()

    @get:JsonSchemaInject(json = """{"examples":["http://localhost:9000"],"order":7}""")
    override val s3Endpoint: String? = null

    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"],\"order\":8}"
    )
    override val s3PathFormat: String? = null

    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"],\"order\":9}"
    )
    override val fileNamePattern: String? = null

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

    @get:JsonProperty("num_part_formatters") val numPartFormatters: Int? = null

    @get:JsonProperty("skip_json_on_proto") val skipJsonOnProto: Boolean? = null

    @get:JsonProperty("disable_uuid") val disableUUID: Boolean? = null

    @get:JsonProperty("disable_mapper") val disableMapper: Boolean? = null

    @get:JsonProperty("use_coded_input_stream") val useCodedInputStream: Boolean? = null

    @get:JsonProperty("use_snappy") val useSnappy: Boolean? = null
}

@Singleton
class S3V2SpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}
