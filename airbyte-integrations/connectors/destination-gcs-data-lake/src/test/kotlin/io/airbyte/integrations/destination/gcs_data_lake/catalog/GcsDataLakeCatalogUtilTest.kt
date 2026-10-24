/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import com.google.auth.oauth2.ServiceAccountCredentials
import com.google.cloud.NoCredentials
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfig
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.PolarisCatalogConfiguration
import io.mockk.mockk
import java.security.KeyPairGenerator
import java.util.Base64
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertIs
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.gcp.GCPProperties
import org.apache.iceberg.gcp.auth.GoogleAuthManager
import org.apache.iceberg.rest.auth.AuthProperties
import org.junit.jupiter.api.Test

internal class GcsDataLakeCatalogUtilTest {
    private val catalogUtil = GcsDataLakeCatalogUtil(mockk<IcebergUtil>(relaxed = true))

    @Test
    fun `BigLake properties use refreshable Google auth without parsing credentials`() {
        val config =
            configuration(
                catalogConfiguration =
                    BigLakeCatalogConfiguration(
                        catalogName = "test-catalog",
                        gcpLocation = "us-central1",
                    ),
            )

        val properties = catalogUtil.toCatalogProperties(config)

        assertEquals(AuthProperties.AUTH_TYPE_GOOGLE, properties[AuthProperties.AUTH_TYPE])
        assertEquals(
            config.serviceAccountJson,
            properties[GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY],
        )
        assertNull(properties["header.Authorization"])
        assertNull(properties[GCPProperties.GCS_OAUTH2_TOKEN])
        assertEquals(GcsDataLakeFileIO::class.java.name, properties[CatalogProperties.FILE_IO_IMPL])
        assertEquals("gs://bucket/warehouse", properties[CatalogProperties.WAREHOUSE_LOCATION])
        assertEquals("project", properties["header.x-goog-user-project"])
        assertEquals("us-central1", properties["gcp.location"])
        assertEquals("projects/project/catalogs/test-catalog", properties["prefix"])
    }

    @Test
    fun `Polaris properties preserve Polaris auth and use the custom FileIO`() {
        val properties =
            catalogUtil.toCatalogProperties(
                configuration(
                    catalogConfiguration =
                        PolarisCatalogConfiguration(
                            serverUri = "https://polaris.example/api/catalog",
                            catalogName = "polaris-catalog",
                            clientId = "clientId",
                            clientSecret = "clientSecret",
                        ),
                ),
            )

        assertNull(properties[AuthProperties.AUTH_TYPE])
        assertNull(properties[GCPProperties.GCS_OAUTH2_TOKEN])
        assertEquals(
            "not valid JSON",
            properties[GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY],
        )
        assertEquals("clientId:clientSecret", properties["credential"])
        assertEquals(GcsDataLakeFileIO::class.java.name, properties[CatalogProperties.FILE_IO_IMPL])
        assertEquals("project", properties[GCPProperties.GCS_PROJECT_ID])
        assertEquals("polaris-catalog", properties[CatalogProperties.WAREHOUSE_LOCATION])
    }

    @Test
    fun `emulator configuration uses NoCredentials and the configured host`() {
        val endpoint = "http://localhost:4443"
        val properties =
            catalogUtil.toCatalogProperties(
                configuration(
                    gcsEndpoint = endpoint,
                    catalogConfiguration =
                        PolarisCatalogConfiguration(
                            serverUri = "https://polaris.example/api/catalog",
                            catalogName = "polaris-catalog",
                            clientId = "clientId",
                            clientSecret = "clientSecret",
                        ),
                ),
            )
        val fileIO = GcsDataLakeFileIO()
        fileIO.initialize(properties)

        try {
            val storage = fileIO.client()
            assertIs<NoCredentials>(storage.options.credentials)
            assertEquals(endpoint, storage.options.host)
        } finally {
            fileIO.close()
        }
    }

    @Test
    fun `service account JSON creates refreshable service account credentials`() {
        val fileIO = GcsDataLakeFileIO()
        fileIO.initialize(
            mapOf(
                GCPProperties.GCS_PROJECT_ID to "project",
                GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY to serviceAccountJson(),
            ),
        )

        try {
            val credentials = fileIO.client().options.credentials
            assertIs<ServiceAccountCredentials>(credentials)
        } finally {
            fileIO.close()
        }
    }

    @Test
    fun `authenticated FileIO requires nonblank credentials JSON`() {
        for (credentialsJson in listOf(null, "", " \n")) {
            val properties = buildMap {
                put(GCPProperties.GCS_PROJECT_ID, "project")
                credentialsJson?.let {
                    put(GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY, it)
                }
            }
            val fileIO = GcsDataLakeFileIO()
            fileIO.initialize(properties)

            try {
                val error = assertFailsWith<IllegalStateException> { fileIO.client() }
                assertTrue(
                    error.message
                        .orEmpty()
                        .contains(GoogleAuthManager.GCP_CREDENTIALS_JSON_PROPERTY),
                )
            } finally {
                fileIO.close()
            }
        }
    }

    private fun configuration(
        serviceAccountJson: String = "not valid JSON",
        gcsEndpoint: String? = null,
        catalogConfiguration: GcsCatalogConfig =
            BigLakeCatalogConfiguration(
                catalogName = "test-catalog",
                gcpLocation = "us-central1",
            ),
    ) =
        GcsDataLakeConfiguration(
            gcsBucketName = "bucket",
            serviceAccountJson = serviceAccountJson,
            gcpProjectId = "project",
            gcpLocation = "us-central1",
            gcsEndpoint = gcsEndpoint,
            namespace = "namespace",
            gcsCatalogConfiguration =
                GcsCatalogConfiguration(
                    warehouseLocation = "gs://bucket/warehouse",
                    mainBranchName = "main",
                    catalogConfiguration = catalogConfiguration,
                ),
        )

    private fun serviceAccountJson(): String {
        val privateKey =
            KeyPairGenerator.getInstance("RSA").apply { initialize(2048) }.generateKeyPair().private
        val encodedKey = Base64.getEncoder().encodeToString(privateKey.encoded)
        val pem =
            "-----BEGIN PRIVATE KEY-----\\n${encodedKey.chunked(64).joinToString("\\n")}\\n-----END PRIVATE KEY-----\\n"

        return """
            {
              "type": "service_account",
              "project_id": "project",
              "private_key_id": "test-key-id",
              "private_key": "$pem",
              "client_email": "test@project.iam.gserviceaccount.com",
              "client_id": "123456789",
              "token_uri": "https://oauth2.googleapis.com/token"
            }
        """
            .trimIndent()
    }
}
