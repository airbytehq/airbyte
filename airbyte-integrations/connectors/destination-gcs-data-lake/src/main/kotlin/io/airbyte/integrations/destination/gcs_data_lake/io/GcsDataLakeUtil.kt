/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.io

import com.google.auth.oauth2.GoogleCredentials
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.NessieCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.PolarisCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.GcsDataLakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogProperties.URI
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_NESSIE
import org.apache.iceberg.CatalogUtil.ICEBERG_CATALOG_TYPE_REST
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.gcp.GCPProperties
import org.apache.iceberg.gcp.gcs.GCSFileIO
import org.projectnessie.client.NessieConfigConstants

private val logger = KotlinLogging.logger {}

/**
 * Collection of Iceberg-related utilities for GCS Data Lake.
 * Configures Iceberg to use GCS as the storage backend with various catalog types.
 */
@Singleton
class GcsDataLakeUtil(
    private val icebergUtil: IcebergUtil,
) {
    /** Filters out any entry from the map that has a null value */
    fun <K, V : Any> mapOfNotNull(vararg pairs: Pair<K, V?>): Map<K, V> =
        pairs.mapNotNull { (k, v) -> v?.let { k to it } }.toMap()

    fun createNamespace(
        streamDescriptor: DestinationStream.Descriptor,
        catalog: Catalog
    ) {
        icebergUtil.createNamespace(streamDescriptor, catalog)
    }

    /**
     * Creates the Iceberg [Catalog] configuration properties from the destination's configuration.
     *
     * @param config The destination's configuration
     * @return The Iceberg [Catalog] configuration properties.
     */
    fun toCatalogProperties(config: GcsDataLakeConfiguration): Map<String, String> {
        val icebergCatalogConfig = config.icebergCatalogConfiguration
        val catalogConfig = icebergCatalogConfig.catalogConfiguration

        // Build base GCS properties
        val gcsProperties = buildGcsProperties(config, icebergCatalogConfig)

        return when (catalogConfig) {
            is NessieCatalogConfiguration ->
                buildNessieProperties(config, catalogConfig, gcsProperties)
            is RestCatalogConfiguration ->
                buildRestProperties(config, catalogConfig, gcsProperties)
            is PolarisCatalogConfiguration ->
                buildPolarisProperties(config, catalogConfig, gcsProperties)
            else ->
                throw IllegalArgumentException(
                    "Unsupported catalog type: ${catalogConfig::class.java.name}"
                )
        }
    }

    /**
     * Builds the base GCS FileIO properties for Iceberg.
     */
    private fun buildGcsProperties(
        config: GcsDataLakeConfiguration,
        icebergCatalogConfig: IcebergCatalogConfiguration,
    ): Map<String, String> {
        return buildMap {
            // Use GCS FileIO implementation
            put(CatalogProperties.FILE_IO_IMPL, GCSFileIO::class.java.name)

            // Set warehouse location
            put(CatalogProperties.WAREHOUSE_LOCATION, icebergCatalogConfig.warehouseLocation)

            // Add GCS project ID if available
            config.projectId?.let { projectId ->
                put(GCPProperties.GCS_PROJECT_ID, projectId)
            }

            // Add optional GCS endpoint if provided (for testing with emulators)
            config.gcsEndpoint?.let { endpoint ->
                put(GCPProperties.GCS_SERVICE_HOST, endpoint)
                put(GCPProperties.GCS_NO_AUTH, "true")  // For emulator testing
            }

            // Configure GCS OAuth2 token
            // The GCSFileIO will use this credential for authentication
            // We pass the service account JSON as a credential source
            put(GCPProperties.GCS_OAUTH2_TOKEN_EXPIRES_AT, Long.MAX_VALUE.toString())
        }
    }

    /**
     * Builds Nessie catalog properties with GCS storage.
     */
    private fun buildNessieProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: NessieCatalogConfiguration,
        gcsProperties: Map<String, String>
    ): Map<String, String> {
        val nessieProperties =
            mapOfNotNull(
                CatalogUtil.ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_NESSIE,
                URI to catalogConfig.serverUri,
                NessieConfigConstants.CONF_NESSIE_REF to
                    config.icebergCatalogConfiguration.mainBranchName,
            )

        val authTokenProperties = buildMap {
            // Add optional Nessie authentication if provided
            catalogConfig.accessToken?.let { token ->
                put(NessieConfigConstants.CONF_NESSIE_AUTH_TYPE, "BEARER")
                put(NessieConfigConstants.CONF_NESSIE_AUTH_TOKEN, token)
            }
        }

        return nessieProperties + gcsProperties + authTokenProperties
    }

    /**
     * Builds REST catalog properties with GCS storage.
     */
    private fun buildRestProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: RestCatalogConfiguration,
        gcsProperties: Map<String, String>
    ): Map<String, String> {
        val restProperties =
            mapOfNotNull(
                CatalogUtil.ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_REST,
                URI to catalogConfig.serverUri,
            )

        return restProperties + gcsProperties
    }

    /**
     * Builds Polaris catalog properties with GCS storage and OAuth2 authentication.
     */
    private fun buildPolarisProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: PolarisCatalogConfiguration,
        gcsProperties: Map<String, String>
    ): Map<String, String> {
        val credential =
            "${requireNotNull(catalogConfig.clientId)}:${requireNotNull(catalogConfig.clientSecret)}"

        val polarisProperties =
            mapOfNotNull(
                CatalogUtil.ICEBERG_CATALOG_TYPE to ICEBERG_CATALOG_TYPE_REST,
                URI to catalogConfig.serverUri,
                "credential" to credential,
                "scope" to "PRINCIPAL_ROLE:ALL",
                CatalogProperties.WAREHOUSE_LOCATION to catalogConfig.catalogName,
            )

        return polarisProperties +
            gcsProperties.filterKeys { it != CatalogProperties.WAREHOUSE_LOCATION }
    }

    /**
     * Gets GoogleCredentials for GCS operations.
     * This is used by GCSFileIO for authentication.
     */
    fun getGoogleCredentials(config: GcsDataLakeConfiguration): GoogleCredentials {
        return config.googleCredentials
    }
}
