/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.gcp.GCPProperties

private val logger = KotlinLogging.logger {}

/**
 * Utility for configuring Apache Iceberg with BigLake catalog on GCS.
 *
 * BigLake can be accessed via two approaches:
 * 1. Direct BigLakeCatalog implementation (org.apache.iceberg.gcp.biglake.BigLakeCatalog)
 * 2. REST catalog API (https://biglake.googleapis.com/v1)
 *
 * This implementation uses the REST catalog approach as it's more standard and compatible
 * with the broader Iceberg ecosystem.
 */
@Singleton
class GcsDataLakeCatalogUtil(
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
     * Creates the Iceberg [Catalog] configuration properties for BigLake.
     *
     * Configures both BigLake REST catalog and GCS FileIO for object storage.
     * Obtains OAuth token from service account and sets it directly in the Authorization header.
     *
     * @param config The destination's configuration
     * @return The Iceberg [Catalog] configuration properties.
     */
    fun toCatalogProperties(config: GcsDataLakeConfiguration): Map<String, String> {
        // Get OAuth2 access token from Google credentials
        val credentials = config.googleCredentials
        credentials.refreshIfExpired()
        val accessToken = credentials.accessToken.tokenValue

        return buildMap {
            // Catalog type: REST (BigLake implements Iceberg REST protocol)
            put(CatalogUtil.ICEBERG_CATALOG_TYPE, CatalogUtil.ICEBERG_CATALOG_TYPE_REST)

            // BigLake REST catalog endpoint with prefix for the specific catalog
            // Format: https://biglake.googleapis.com/iceberg/v1/restcatalog/projects/{project}/catalogs/{catalog}
            val catalogPrefix = "projects/${config.projectId}/catalogs/${config.catalogName}"
            put(CatalogProperties.URI, "https://biglake.googleapis.com/iceberg/v1/restcatalog")
            put("prefix", catalogPrefix)

            // Set OAuth Bearer token directly in Authorization header
            // This bypasses GoogleAuthManager and directly authenticates REST requests
            put("header.Authorization", "Bearer $accessToken")

            // User project header for billing
            put("header.x-goog-user-project", config.projectId)

            // GCS FileIO configuration
            put(CatalogProperties.FILE_IO_IMPL, "org.apache.iceberg.gcp.gcs.GCSFileIO")
            put(CatalogProperties.WAREHOUSE_LOCATION, config.warehouseLocation)

            // GCP configuration
            put(GCPProperties.GCS_PROJECT_ID, config.projectId)

            // Pass credentials JSON directly to GCSFileIO
            put(GCPProperties.GCS_OAUTH2_TOKEN, accessToken)

            config.gcsEndpoint?.let { endpoint ->
                put(GCPProperties.GCS_SERVICE_HOST, endpoint)
                put(GCPProperties.GCS_NO_AUTH, "true")  // For emulator testing
            }

            // BigLake-specific properties
            put("gcp.location", config.gcpLocation)
        }
    }
}
