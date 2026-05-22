/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import com.google.auth.oauth2.AccessToken
import com.google.auth.oauth2.OAuth2CredentialsWithRefresh
import com.google.cloud.NoCredentials
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import jakarta.inject.Singleton
import java.util.Date
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.gcp.GCPProperties
import org.apache.iceberg.gcp.gcs.GCSFileIO
import org.apache.iceberg.io.DelegateFileIO
import org.apache.iceberg.io.FileInfo
import org.apache.iceberg.io.InputFile
import org.apache.iceberg.io.OutputFile

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
    companion object {
        const val GCS_DATA_LAKE_FILE_IO_IMPL =
            "io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeFileIO"
    }

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
        val credentials = config.googleCredentials
        credentials.refreshIfExpired()
        val accessToken = credentials.accessToken.tokenValue
        config.configureFileIO()

        val catalogConfig = config.gcsCatalogConfiguration

        val gcsProperties = buildGcsProperties(config, catalogConfig)

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
    ): Map<String, String> {
        return buildMap {
            put(CatalogProperties.FILE_IO_IMPL, GCS_DATA_LAKE_FILE_IO_IMPL)
            put(CatalogProperties.WAREHOUSE_LOCATION, catalogConfig.warehouseLocation)

            put(GCPProperties.GCS_PROJECT_ID, config.projectId)

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

class GcsDataLakeFileIO : DelegateFileIO {
    private lateinit var delegate: GCSFileIO
    private lateinit var properties: Map<String, String>

    override fun initialize(properties: Map<String, String>) {
        this.properties = properties.toMap()
        delegate =
            GCSFileIO(
                {
                    val config = GcsDataLakeFileIOConfig.get()
                    StorageOptions.newBuilder()
                        .apply {
                            setProjectId(config.projectId)
                            config.serviceHost?.let { setHost(it) }
                            if (config.serviceHost.isNullOrEmpty()) {
                                setCredentials(
                                    OAuth2CredentialsWithRefresh.newBuilder()
                                        .setAccessToken(config.accessToken())
                                        .setRefreshHandler { config.accessToken() }
                                        .build()
                                )
                            } else {
                                setCredentials(NoCredentials.getInstance())
                            }
                        }
                        .build()
                        .service
                },
                GCPProperties(properties),
            )
    }

    override fun newInputFile(path: String): InputFile = delegate.newInputFile(path)

    override fun newInputFile(path: String, length: Long): InputFile =
        delegate.newInputFile(path, length)

    override fun newOutputFile(path: String): OutputFile = delegate.newOutputFile(path)

    override fun deleteFile(path: String) {
        delegate.deleteFile(path)
    }

    override fun listPrefix(prefix: String): Iterable<FileInfo> = delegate.listPrefix(prefix)

    override fun deletePrefix(prefix: String) {
        delegate.deletePrefix(prefix)
    }

    override fun deleteFiles(paths: Iterable<String>) {
        delegate.deleteFiles(paths)
    }

    override fun properties(): Map<String, String> = properties

    fun client(): com.google.cloud.storage.Storage = delegate.client()

    override fun close() {
        delegate.close()
    }
}

internal data class GcsDataLakeFileIOConfig(
    val projectId: String,
    val serviceHost: String?,
    val accessToken: () -> AccessToken,
) {
    companion object {
        private val currentConfig = AtomicReference<GcsDataLakeFileIOConfig>()

        fun set(config: GcsDataLakeFileIOConfig) {
            currentConfig.set(config)
        }

        fun get(): GcsDataLakeFileIOConfig =
            checkNotNull(currentConfig.get()) {
                "GCS Data Lake FileIO credentials are not configured."
            }
    }
}

private fun GcsDataLakeConfiguration.configureFileIO() {
    GcsDataLakeFileIOConfig.set(
        GcsDataLakeFileIOConfig(
            projectId = projectId,
            serviceHost = gcsEndpoint,
            accessToken = {
                googleCredentials.refresh()
                val token = googleCredentials.accessToken
                AccessToken(
                    token.tokenValue,
                    token.expirationTime
                        ?: Date(System.currentTimeMillis() + TimeUnit.HOURS.toMillis(1))
                )
            }
        )
    )
}
