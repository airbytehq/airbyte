/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.iceberg.parquet.RestCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeFileIO
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsStorageSupplier
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsRestCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.RestCatalogSpec
import io.mockk.mockk
import org.apache.iceberg.CatalogProperties
import org.apache.iceberg.CatalogUtil
import org.apache.iceberg.gcp.GCPProperties
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class GcsRestCatalogTest {
    private val util = GcsDataLakeCatalogUtil(mockk())

    private fun properties(rest: RestCatalogConfiguration): Map<String, String> =
        util.toCatalogProperties(
            GcsDataLakeConfiguration(
                gcsBucketName = "bucket",
                serviceAccountJson = "{}",
                gcpProjectId = "project",
                gcpLocation = "us",
                gcsEndpoint = "http://localhost:9023",
                namespace = rest.namespace,
                gcsCatalogConfiguration =
                    GcsCatalogConfiguration(
                        "gs://bucket/warehouse",
                        "main",
                        GcsRestCatalogConfiguration(rest),
                    ),
            ),
        )

    @Test
    fun `REST uses GCS file IO without refreshing catalog credentials`() {
        val props = properties(RestCatalogConfiguration("https://catalog", "schema"))
        assertEquals(CatalogUtil.ICEBERG_CATALOG_TYPE_REST, props[CatalogUtil.ICEBERG_CATALOG_TYPE])
        assertEquals(GcsDataLakeFileIO::class.java.name, props[CatalogProperties.FILE_IO_IMPL])
        assertEquals("gs://bucket/warehouse", props["warehouse"])
        assertEquals("http://localhost:9023", props[GCPProperties.GCS_SERVICE_HOST])
        assertFalse(props.containsKey("token"))
        assertFalse(props.containsKey("credential"))
    }

    @Test
    fun `REST maps token and warehouse independently from storage`() {
        val props =
            properties(
                RestCatalogConfiguration(
                    "https://catalog",
                    "schema",
                    warehouse = "uc",
                    token = "token",
                ),
            )
        assertEquals("uc", props["warehouse"])
        assertEquals("token", props["token"])
        assertEquals("https://catalog", props["uri"])
    }

    @Test
    fun `REST maps OAuth and namespace fallback`() {
        val spec =
            RestCatalogSpec(
                serverUri = "https://catalog",
                clientId = "id",
                clientSecret = "secret",
                oauth2ServerUri = "https://catalog/token",
                scope = "all-apis",
            )
        val rest = spec.toConfiguration("default")
        assertEquals("default", rest.namespace)
        assertEquals(
            "schema",
            RestCatalogSpec(serverUri = "https://catalog", namespace = "schema")
                .toConfiguration("default")
                .namespace,
        )
        val props = properties(rest)
        assertEquals("id:secret", props["credential"])
        assertEquals("https://catalog/token", props["oauth2-server-uri"])
        assertEquals("all-apis", props["scope"])
        assertFalse(props.containsKey("token"))
    }

    @Test
    fun `GCS file IO initializes storage independently of REST bearer credentials`() {
        val props =
            properties(RestCatalogConfiguration("https://catalog", "schema", token = "token"))
        GcsDataLakeFileIO().use { io ->
            io.initialize(props)
            assertEquals(props, io.properties())
            assertEquals(
                "gs://bucket/file.parquet",
                io.newInputFile("gs://bucket/file.parquet").location(),
            )
            assertEquals(
                "gs://bucket/output.parquet",
                io.newOutputFile("gs://bucket/output.parquet").location(),
            )
        }
    }

    @Test
    fun `GCS storage requires service account credentials unless using an emulator`() {
        assertThrows(IllegalStateException::class.java) {
            GcsStorageSupplier("project", null, false, null).get()
        }
    }
}
