/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.iceberg.parquet.GlueCatalogConfiguration
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class AirbyteContextStoreConfigurationFactoryTest {
    private val factory = AirbyteContextStoreConfigurationFactory()

    private fun specFrom(json: String) =
        Jsons.readValue(json, AirbyteContextStoreSpecification::class.java)

    @Test
    fun `builds the data lake configuration from the values injected by airbyte`() {
        val spec =
            specFrom(
                """
                {
                  "acknowledge_managed_storage": true,
                  "access_key_id": "some-access-key-id",
                  "secret_access_key": "some-secret-access-key",
                  "s3_bucket_name": "airbyte-managed-bucket",
                  "s3_bucket_region": "us-west-2",
                  "warehouse_location": "s3://airbyte-managed-bucket/tenant-prefix",
                  "main_branch_name": "main",
                  "flush_batch_size_mb": 50,
                  "catalog_type": {
                    "catalog_type": "GLUE",
                    "glue_id": "123456789012",
                    "database_name": "sonar_airbyte_hosted",
                    "role_arn": "arn:aws:iam::123456789012:role/airbyte-managed"
                  }
                }
                """.trimIndent()
            )

        val config = factory.makeWithoutExceptionHandling(spec)

        assertEquals("some-access-key-id", config.awsAccessKeyConfiguration.accessKeyId)
        assertEquals("airbyte-managed-bucket", config.s3BucketConfiguration.s3BucketName)
        assertEquals("us-west-2", config.s3BucketConfiguration.s3BucketRegion)
        assertEquals(
            "s3://airbyte-managed-bucket/tenant-prefix",
            config.icebergCatalogConfiguration.warehouseLocation
        )
        val catalog =
            config.icebergCatalogConfiguration.catalogConfiguration as GlueCatalogConfiguration
        assertEquals("123456789012", catalog.glueId)
        assertEquals("sonar_airbyte_hosted", catalog.databaseName)
        assertEquals(
            "arn:aws:iam::123456789012:role/airbyte-managed",
            catalog.awsArnRoleConfiguration.roleArn
        )
        assertEquals(50L, config.flushBatchSizeMb)
    }

    @Test
    fun `rejects a config that has not acknowledged managed storage`() {
        val spec = specFrom("""{"acknowledge_managed_storage": false}""")

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun `rejects a config that airbyte did not supply storage values for`() {
        val spec = specFrom("""{"acknowledge_managed_storage": true}""")

        assertThrows(SystemErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun `rejects a config that airbyte did not supply a region for`() {
        val spec =
            specFrom(
                """
                {
                  "acknowledge_managed_storage": true,
                  "s3_bucket_name": "airbyte-managed-bucket",
                  "warehouse_location": "s3://airbyte-managed-bucket/tenant-prefix",
                  "main_branch_name": "main",
                  "catalog_type": {
                    "catalog_type": "GLUE",
                    "glue_id": "123456789012",
                    "database_name": "sonar_airbyte_hosted"
                  }
                }
                """.trimIndent()
            )

        assertThrows(SystemErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun `rejects a config that airbyte did not supply catalog values for`() {
        val spec =
            specFrom(
                """
                {
                  "acknowledge_managed_storage": true,
                  "s3_bucket_name": "airbyte-managed-bucket",
                  "s3_bucket_region": "us-west-2",
                  "warehouse_location": "s3://airbyte-managed-bucket/tenant-prefix",
                  "main_branch_name": "main",
                  "catalog_type": {
                    "catalog_type": "GLUE",
                    "glue_id": "",
                    "database_name": ""
                  }
                }
                """.trimIndent()
            )

        assertThrows(SystemErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }
}
