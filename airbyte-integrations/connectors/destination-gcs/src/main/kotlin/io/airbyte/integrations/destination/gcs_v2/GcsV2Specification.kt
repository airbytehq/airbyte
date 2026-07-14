/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.gcs.GcsAuthSpecification
import io.airbyte.cdk.load.command.gcs.GcsCommonSpecification
import io.airbyte.cdk.load.command.gcs.GcsHmacKeySpecification
import io.airbyte.cdk.load.command.gcs.GcsRegion
import io.airbyte.cdk.load.command.gcs.GcsRegionSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedAvroFormatSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedObjectStorageFormatSpecification
import io.airbyte.cdk.load.command.object_storage.DeprecatedObjectStorageFormatSpecificationProvider
import io.airbyte.cdk.load.command.object_storage.ObjectStoragePathConfiguration
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.integrations.destination.gcs_v2.GcsV2Specification.Companion.DEFAULT_FILE_FORMAT
import io.airbyte.integrations.destination.gcs_v2.GcsV2Specification.Companion.DEFAULT_PATH_FORMAT
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

/**
 * GCS destination connector specification.
 *
 * Composes [GcsCommonSpecification] (bucket, path, HMAC credential), [GcsRegionSpecification], and
 * [DeprecatedObjectStorageFormatSpecificationProvider] (Avro/CSV/JSONL/Parquet). Additionally
 * declares `gcs_path_format` and `file_name_pattern` for customizable output paths.
 *
 * Both path fields are nullable for backward compatibility with v0.4.x configs; when null,
 * [toObjectStoragePathConfiguration] falls back to [DEFAULT_PATH_FORMAT] / [DEFAULT_FILE_FORMAT].
 */
@Singleton
@JsonSchemaTitle("GCS V2 Destination Spec")
@JsonSchemaInject()
class GcsV2Specification :
    ConfigurationSpecification(),
    GcsCommonSpecification,
    GcsRegionSpecification,
    DeprecatedObjectStorageFormatSpecificationProvider {

    @get:JsonSchemaInject(json = """{"order":0}""")
    override val credential: GcsAuthSpecification = GcsHmacKeySpecification("", "")

    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":1}""")
    override val gcsBucketName: String = ""

    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"],"order":2}""")
    override val path: String = ""

    @get:JsonSchemaInject(json = """{"examples":["us"],"order":3,"default":"us"}""")
    override val gcsBucketRegion: GcsRegion? = GcsRegion.US

    @get:JsonSchemaInject(json = """{"order":4}""")
    override val format: DeprecatedObjectStorageFormatSpecification =
        DeprecatedAvroFormatSpecification()

    @get:JsonSchemaTitle("GCS Path Format")
    @get:JsonPropertyDescription(
        "Format string on how data will be organized inside the GCS bucket directory. " +
            "Available variables: \${NAMESPACE}, \${STREAM_NAME}, \${YEAR}, \${MONTH}, " +
            "\${DAY}, \${HOUR}, \${MINUTE}, \${SECOND}, \${MILLISECOND}, \${EPOCH}, " +
            "\${UUID}, \${SYNC_ID}.",
    )
    @get:JsonSchemaInject(
        json =
            "{\"order\":5,\"default\":\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"}",
    )
    @get:JsonProperty("gcs_path_format")
    val gcsPathFormat: String? = DEFAULT_PATH_FORMAT

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription(
        "Pattern for output file names in the bucket directory. " +
            "Available variables: {date} (yyyy_MM_dd), {date:yyyy_MM}, " +
            "{timestamp}, {part_number}, {sync_id}, {format_extension}.",
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"],\"order\":6,\"default\":\"{part_number}{format_extension}\"}",
    )
    @get:JsonProperty("file_name_pattern")
    val fileNamePattern: String? = DEFAULT_FILE_FORMAT

    /** Converts spec path fields to [ObjectStoragePathConfiguration], with null-safe defaults. */
    fun toObjectStoragePathConfiguration(): ObjectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = path,
            pathPattern = gcsPathFormat ?: DEFAULT_PATH_FORMAT,
            fileNamePattern = fileNamePattern ?: DEFAULT_FILE_FORMAT,
            resolveNamesMethod = { Transformations.toS3SafeCharacters(it) },
        )

    companion object {
        const val DEFAULT_PATH_FORMAT =
            "\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_"
        const val DEFAULT_FILE_FORMAT = "{part_number}{format_extension}"
    }
}

@Singleton
class GcsV2SpecificationExtension : DestinationSpecificationExtension {

    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}
