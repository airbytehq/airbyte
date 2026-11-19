/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
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
 * Declares bucket, path and [credential], and composes [GcsRegionSpecification] and
 * [DeprecatedObjectStorageFormatSpecificationProvider] (Avro/CSV/JSONL/Parquet). Additionally
 * declares `gcs_path_format` and `file_name_pattern` for customizable output paths.
 *
 * Bucket, path and credential mirror the CDK's `GcsCommonSpecification` (same JSON names, titles
 * and descriptions, so HMAC configs are unchanged), but [credential] is typed as the connector's
 * [GcsV2AuthSpecification] so it can also offer Workload Identity Federation. The CDK's
 * `GcsAuthSpecification` is sealed and HMAC-only.
 *
 * Both path fields are nullable for backward compatibility with v0.4.x configs; when null or blank
 * (for example a cleared optional field in the UI), [toObjectStoragePathConfiguration] falls back
 * to [DEFAULT_PATH_FORMAT] / [DEFAULT_FILE_FORMAT].
 */
@Singleton
@JsonSchemaTitle("GCS V2 Destination Spec")
@JsonSchemaInject()
class GcsV2Specification :
    ConfigurationSpecification(),
    GcsRegionSpecification,
    DeprecatedObjectStorageFormatSpecificationProvider {

    @get:JsonSchemaTitle("Credential")
    @get:JsonPropertyDescription(
        """How to authenticate with Cloud Storage. An <a href="https://cloud.google.com/storage/docs/authentication/hmackeys">HMAC key</a> is a long-lived credential for a service account or user account. <a href="https://cloud.google.com/iam/docs/workload-identity-federation">Workload Identity Federation</a> exchanges a token from an external identity provider for short-lived Google credentials, so no Google key is stored in Airbyte.""",
    )
    @get:JsonProperty("credential")
    @get:JsonSchemaInject(json = """{"order":0}""")
    val credential: GcsV2AuthSpecification = GcsV2HmacKeySpecification("", "")

    @get:JsonSchemaTitle("GCS Bucket Name")
    @get:JsonPropertyDescription(
        """The name of the GCS bucket. Read more <a href="https://cloud.google.com/storage/docs/naming-buckets">here</a>.""",
    )
    @get:JsonProperty("gcs_bucket_name")
    @get:JsonSchemaInject(json = """{"examples":["airbyte_sync"],"order":1}""")
    val gcsBucketName: String = ""

    @get:JsonSchemaTitle("GCS Bucket Path")
    @get:JsonPropertyDescription("Directory under the GCS bucket where data will be written.")
    @get:JsonProperty("gcs_bucket_path")
    @get:JsonSchemaInject(json = """{"examples":["data_sync/test"],"order":2}""")
    val path: String = ""

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

    /**
     * Converts spec path fields to [ObjectStoragePathConfiguration], defaulting null/blank fields.
     */
    fun toObjectStoragePathConfiguration(): ObjectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = path,
            pathPattern = gcsPathFormat.orDefault(DEFAULT_PATH_FORMAT),
            fileNamePattern = fileNamePattern.orDefault(DEFAULT_FILE_FORMAT),
            resolveNamesMethod = { Transformations.toS3SafeCharacters(it) },
        )

    private fun String?.orDefault(default: String): String = if (isNullOrBlank()) default else this

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
