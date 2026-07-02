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
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

/**
 * Mirror of S3V2Specification. Swaps the AWS mixins (AWSAccessKeySpecification /
 * AWSArnRoleSpecification / S3BucketSpecification / S3PathSpecification) for the GCS ones:
 * - [GcsCommonSpecification] -> gcs_bucket_name, gcs_bucket_path (`path`), credential (HMAC oneOf)
 * - [GcsRegionSpecification] -> gcs_bucket_region ([GcsRegion] enum, default "us")
 * - [DeprecatedObjectStorageFormatSpecificationProvider] -> Avro/CSV/JSONL/Parquet format oneOf
 *
 * There is no role_arn (GCS has no STS) and credential is HMAC-only, matching v0.4.x drop-in
 * config.
 *
 * GAP-FILLER: legacy-task-load-gcs has no path-format / file-name-pattern spec (unlike
 * S3PathSpecification), so `gcs_path_format` + `file_name_pattern` are declared here and lowered to
 * the generic [ObjectStoragePathConfiguration] via [toObjectStoragePathConfiguration], using the
 * SAME [Transformations.toS3SafeCharacters] transform S3 uses — keeping path/partition behavior
 * identical to destination-s3 and to the v0.4.x directory-per-stream layout. Both new fields are
 * optional (null default) so existing v0.4.x configs remain valid.
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
    // v0.4.x default output format is AVRO; keep it the default so migrated configs behave
    // identically.
    DeprecatedAvroFormatSpecification()

    @get:JsonSchemaTitle("GCS Path Format")
    @get:JsonPropertyDescription(
        "Format string on how data will be organized inside the GCS bucket directory."
    )
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"\${NAMESPACE}/\${STREAM_NAME}/\${YEAR}_\${MONTH}_\${DAY}_\${EPOCH}_\"],\"order\":5}"
    )
    @get:JsonProperty("gcs_path_format")
    val gcsPathFormat: String? = null

    @get:JsonSchemaTitle("File Name Pattern")
    @get:JsonPropertyDescription("Pattern to match file names in the bucket directory.")
    @get:JsonSchemaInject(
        json =
            "{\"examples\":[\"{date}\",\"{date:yyyy_MM}\",\"{timestamp}\",\"{part_number}\",\"{sync_id}\"],\"order\":6}"
    )
    @get:JsonProperty("file_name_pattern")
    val fileNamePattern: String? = null

    /**
     * Lower the GCS bucket path + (optional) path/file-name patterns to the generic object-storage
     * path config. `path` (gcs_bucket_path) comes from [GcsCommonSpecification]. When
     * `gcsPathFormat` is null the CDK's
     * [io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory] applies its
     * DEFAULT_PATH_FORMAT (${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/${'$'}{YEAR}_...), matching
     * v0.4.x.
     */
    fun toObjectStoragePathConfiguration(): ObjectStoragePathConfiguration =
        ObjectStoragePathConfiguration(
            prefix = path,
            pathPattern = gcsPathFormat,
            fileNamePattern = fileNamePattern,
            resolveNamesMethod = { Transformations.toS3SafeCharacters(it) },
        )
}

@Singleton
class GcsV2SpecificationExtension : DestinationSpecificationExtension {
    // Match v0.4.x: supported_destination_sync_modes = [overwrite, append].
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
        )
    override val supportsIncremental = true
}
