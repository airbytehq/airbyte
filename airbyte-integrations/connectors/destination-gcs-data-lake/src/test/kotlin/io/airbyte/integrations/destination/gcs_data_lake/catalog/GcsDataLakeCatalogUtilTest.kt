/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import com.google.auth.oauth2.AccessToken
import com.google.auth.oauth2.GoogleCredentials
import com.google.auth.oauth2.OAuth2CredentialsWithRefresh
import com.google.cloud.NoCredentials
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import io.mockk.every
import io.mockk.mockk
import java.util.Date
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.gcp.GCPProperties
import org.junit.jupiter.api.Test

class GcsDataLakeCatalogUtilTest {
    private val util =
        GcsDataLakeCatalogUtil(
            IcebergUtil(SimpleTableIdGenerator("namespace"), AirbyteValueCoercer())
        )

    @Test
    fun `GCS properties use refresh-capable FileIO instead of static OAuth token`() {
        val properties = util.toCatalogProperties(gcsConfiguration())

        assertEquals(
            GcsDataLakeCatalogUtil.GCS_DATA_LAKE_FILE_IO_IMPL,
            properties[CatalogProperties.FILE_IO_IMPL],
        )
        assertFalse(properties.containsKey(GCPProperties.GCS_OAUTH2_TOKEN))

        val fileIO = GcsDataLakeFileIO()
        fileIO.initialize(properties)
        val storageCredentials = fileIO.client().options.credentials
        assertIs<OAuth2CredentialsWithRefresh>(storageCredentials)
    }

    @Test
    fun `BigLake catalog still includes catalog authorization header`() {
        val properties =
            util.toCatalogProperties(
                gcsConfiguration(
                    catalogConfiguration = BigLakeCatalogConfiguration("catalog", "us")
                )
            )

        assertTrue(properties.getValue("header.Authorization").startsWith("Bearer "))
        assertEquals("project-id", properties["header.x-goog-user-project"])
        assertEquals("us", properties["gcp.location"])
    }

    @Test
    fun `local emulator uses no auth and custom service host`() {
        val properties =
            util.toCatalogProperties(
                gcsConfiguration(gcsEndpoint = "http://gcs:4443") // # ignore-https-check
            )

        assertEquals(
            "http://gcs:4443",
            properties[GCPProperties.GCS_SERVICE_HOST]
        ) // # ignore-https-check
        assertEquals("true", properties[GCPProperties.GCS_NO_AUTH])

        val fileIO = GcsDataLakeFileIO()
        fileIO.initialize(properties)
        val storageCredentials = fileIO.client().options.credentials
        assertEquals(NoCredentials.getInstance(), storageCredentials)
    }

    private fun gcsConfiguration(
        catalogConfiguration:
            io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfig =
            PolarisCatalogConfiguration(
                serverUri = "http://polaris:8181", // # ignore-https-check
                catalogName = "catalog",
                clientId = "client-id",
                clientSecret = "client-secret",
            ),
        gcsEndpoint: String? = null,
    ): GcsDataLakeConfiguration {
        val credentials =
            mockk<GoogleCredentials> {
                every { refreshIfExpired() } returns Unit
                every { refresh() } returns Unit
                every { accessToken } returns AccessToken("token", Date(System.currentTimeMillis()))
            }

        return mockk<GcsDataLakeConfiguration> {
            every { googleCredentials } returns credentials
            every { projectId } returns "project-id"
            every { this@mockk.gcsEndpoint } returns gcsEndpoint
            every { gcsCatalogConfiguration } returns
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://bucket/warehouse",
                    mainBranchName = "main",
                    catalogConfiguration = catalogConfiguration,
                )
        }
    }
}
