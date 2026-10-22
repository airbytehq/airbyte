/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.spec

import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.ServiceAccountCredentials
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.nio.charset.StandardCharsets
import java.util.UUID

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_TABLE = "airbyte_test_table"

fun generateStagingBranchName(stream: io.airbyte.cdk.load.command.DestinationStream): String {
    val branchKey =
        listOf(
                stream.mappedDescriptor.namespace.orEmpty(),
                stream.mappedDescriptor.name,
                stream.generationId.toString(),
                stream.minimumGenerationId.toString(),
            )
            .joinToString(":")
    val suffix =
        UUID.nameUUIDFromBytes(branchKey.toByteArray(StandardCharsets.UTF_8))
            .toString()
            .replace("-", "_")
    return "${DEFAULT_STAGING_BRANCH}_$suffix"
}

data class GcsDataLakeConfiguration(
    val gcsBucketName: String,
    val serviceAccountJson: String,
    val gcpProjectId: String?,
    val gcpLocation: String,
    val gcsEndpoint: String?,
    val namespace: String,
    val gcsCatalogConfiguration: GcsCatalogConfiguration,
    val tableFormatVersion: IcebergTableFormatVersion = IcebergTableFormatVersion.V2,
    val icebergDeleteFileType: IcebergDeleteFileType = IcebergDeleteFileType.AUTOMATIC,
    val allowNonReversibleUpgrades: AllowNonReversibleUpgrades = AllowNonReversibleUpgrades.NO,
    val optimizePriorIcebergDeleteFiles: Boolean = true,
    val maxRecordsPerFlush: Long? = null,
) : DestinationConfiguration() {

    object Defaults {
        const val MAX_RECORDS_PER_FLUSH = 10_000_000_000L
    }

    init {
        if (
            icebergDeleteFileType == IcebergDeleteFileType.POSITIONAL &&
                tableFormatVersion == IcebergTableFormatVersion.V3
        ) {
            throw ConfigErrorException(
                "POSITIONAL delete files cannot be written to Iceberg format v3 tables. " +
                "Use DELETION_VECTOR or AUTOMATIC with table_format_version v3.",
            )
        }
        if (
            icebergDeleteFileType == IcebergDeleteFileType.EQUALITY &&
                tableFormatVersion == IcebergTableFormatVersion.V3
        ) {
            throw ConfigErrorException(
                "EQUALITY delete files cannot be written to Iceberg format v3 tables. " +
                    "Use DELETION_VECTOR or AUTOMATIC with table_format_version v3.",
            )
        }
        if (
            icebergDeleteFileType == IcebergDeleteFileType.DELETION_VECTOR &&
                tableFormatVersion == IcebergTableFormatVersion.V2
        ) {
            throw ConfigErrorException(
                "DELETION_VECTOR delete files require Iceberg format v3 tables. " +
                    "Use POSITIONAL, EQUALITY, or AUTOMATIC with table_format_version v2.",
            )
        }
    }

    val resolvedMaxRecordsPerFlush: Long
        get() {
            val records = maxRecordsPerFlush ?: Defaults.MAX_RECORDS_PER_FLUSH
            require(records > 0) { "max_records_per_flush must be positive, got $records" }
            return records
        }

    // Lazy-loaded credentials from service account JSON with proper OAuth scopes
    val googleCredentials: GoogleCredentials by lazy {
        val credentialsStream = ByteArrayInputStream(serviceAccountJson.toByteArray())
        val baseCredentials = GoogleCredentials.fromStream(credentialsStream)

        // Create scoped credentials for GCS and BigQuery access
        baseCredentials.createScoped(
            listOf(
                "https://www.googleapis.com/auth/cloud-platform", // Full GCP access
                "https://www.googleapis.com/auth/devstorage.read_write", // GCS read/write
                "https://www.googleapis.com/auth/bigquery", // BigQuery/BigLake access
            ),
        )
    }

    // Extract project ID - use configured value or extract from service account
    val projectId: String by lazy {
        gcpProjectId
            ?: run {
                val credentials = googleCredentials
                if (credentials is ServiceAccountCredentials) {
                    credentials.projectId
                } else {
                    throw IllegalStateException(
                        "Could not determine GCP project ID from credentials. Please provide gcp_project_id explicitly.",
                    )
                }
            }
    }
}

@Singleton
class GcsDataLakeConfigurationFactory :
    DestinationConfigurationFactory<GcsDataLakeSpecification, GcsDataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: GcsDataLakeSpecification,
    ): GcsDataLakeConfiguration {
        return GcsDataLakeConfiguration(
            gcsBucketName = pojo.gcsBucketName,
            serviceAccountJson = pojo.serviceAccountJson,
            gcpProjectId = pojo.gcpProjectId,
            gcpLocation = pojo.gcpLocation,
            gcsEndpoint = pojo.gcsEndpoint,
            namespace = pojo.namespace,
            gcsCatalogConfiguration = pojo.toGcsCatalogConfiguration(),
            tableFormatVersion = pojo.tableFormatVersion ?: IcebergTableFormatVersion.V2,
            icebergDeleteFileType = pojo.icebergDeleteFileType ?: IcebergDeleteFileType.AUTOMATIC,
            allowNonReversibleUpgrades =
                pojo.allowNonReversibleUpgrades ?: AllowNonReversibleUpgrades.NO,
            optimizePriorIcebergDeleteFiles = pojo.optimizePriorIcebergDeleteFiles ?: true,
            maxRecordsPerFlush = pojo.maxRecordsPerFlush,
        )
    }
}

@Factory
class GcsDataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): GcsDataLakeConfiguration {
        return config as GcsDataLakeConfiguration
    }
}
