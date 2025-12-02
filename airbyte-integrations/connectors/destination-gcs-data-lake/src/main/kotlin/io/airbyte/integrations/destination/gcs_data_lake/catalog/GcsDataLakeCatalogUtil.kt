/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import jakarta.inject.Singleton
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.gcp.GCPProperties

/**
 * Utility for configuring Apache Iceberg with various catalog types on GCS.
 *
 * Supports:
 * - BigLake: Google Cloud's Iceberg REST catalog
 * - Polaris: Apache Polaris catalog
 */
@Singleton
class GcsDataLakeCatalogUtil(
    private val icebergUtil: IcebergUtil,
) {
    fun <K, V : Any> mapOfNotNull(vararg pairs: Pair<K, V?>): Map<K, V> =
        pairs.mapNotNull { (k, v) -> v?.let { k to it } }.toMap()

    fun createNamespace(streamDescriptor: DestinationStream.Descriptor, catalog: Catalog) {
        icebergUtil.createNamespace(streamDescriptor, catalog)
    }

    /**
     * Creates the Iceberg [Catalog] configuration properties from the destination's configuration.
     *
     * @param config The destination's configuration
     * @return The Iceberg [Catalog] configuration properties.
     */
    fun toCatalogProperties(config: GcsDataLakeConfiguration): Map<String, String> {
        // Get OAuth2 access token from Google credentials
        val credentials = config.googleCredentials
        credentials.refreshIfExpired()
        val accessToken = credentials.accessToken.tokenValue

        val catalogConfig = config.gcsCatalogConfiguration

        val gcsProperties = buildGcsProperties(config, catalogConfig, accessToken)

        return when (val catalogConfiguration = catalogConfig.catalogConfiguration) {
            is BigLakeCatalogConfiguration ->
                buildBigLakeProperties(config, catalogConfiguration, gcsProperties, accessToken)
            is PolarisCatalogConfiguration ->
                buildPolarisProperties(catalogConfiguration, gcsProperties)
        }
    }

    private fun buildGcsProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig:
            io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration,
        accessToken: String
    ): Map<String, String> {
        return buildMap {
            put(CatalogProperties.FILE_IO_IMPL, "org.apache.iceberg.gcp.gcs.GCSFileIO")
            put(CatalogProperties.WAREHOUSE_LOCATION, catalogConfig.warehouseLocation)

            // GCP configuration
            put(GCPProperties.GCS_PROJECT_ID, config.projectId)
            put(GCPProperties.GCS_OAUTH2_TOKEN, accessToken)

            // Add optional GCS endpoint if provided (for emulator testing)
            config.gcsEndpoint?.let { endpoint ->
                put(GCPProperties.GCS_SERVICE_HOST, endpoint)
                put(GCPProperties.GCS_NO_AUTH, "true")
            }
        }
    }

    private fun buildBigLakeProperties(
        config: GcsDataLakeConfiguration,
        catalogConfig: BigLakeCatalogConfiguration,
        gcsProperties: Map<String, String>,
        accessToken: String
    ): Map<String, String> {
        val bigLakeProperties =
            mapOfNotNull(
                CatalogUtil.ICEBERG_CATALOG_TYPE to CatalogUtil.ICEBERG_CATALOG_TYPE_REST,
                CatalogProperties.URI to "https://biglake.googleapis.com/iceberg/v1/restcatalog",
                "prefix" to "projects/${config.projectId}/catalogs/${catalogConfig.catalogName}",
                "header.Authorization" to "Bearer $accessToken",
                "header.x-goog-user-project" to config.projectId,
                "gcp.location" to catalogConfig.gcpLocation,
            )

        return bigLakeProperties + gcsProperties
    }

    private fun buildPolarisProperties(
        catalogConfig: PolarisCatalogConfiguration,
        gcsProperties: Map<String, String>
    ): Map<String, String> {
        val credential = "${catalogConfig.clientId}:${catalogConfig.clientSecret}"
        val polarisProperties =
            mapOfNotNull(
                CatalogUtil.ICEBERG_CATALOG_TYPE to CatalogUtil.ICEBERG_CATALOG_TYPE_REST,
                CatalogProperties.URI to catalogConfig.serverUri,
                "credential" to credential,
                "scope" to "PRINCIPAL_ROLE:ALL",
                CatalogProperties.WAREHOUSE_LOCATION to catalogConfig.catalogName,
            )

        return polarisProperties +
            gcsProperties.filterKeys { it != CatalogProperties.WAREHOUSE_LOCATION }
    }
}
