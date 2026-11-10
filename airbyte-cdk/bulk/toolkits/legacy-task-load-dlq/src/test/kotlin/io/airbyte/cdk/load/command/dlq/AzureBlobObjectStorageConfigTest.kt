/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.dlq

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class AzureBlobObjectStorageConfigTest {
    private fun config(fields: String): AzureBlobObjectStorageConfig<*> =
        assertInstanceOf(
            AzureBlobObjectStorageConfig::class.java,
            ValidatedJsonUtils.parseOne(
                    ObjectStorageSpec::class.java,
                    """{
                        "storage_type":"AzureBlob",
                        "azure_blob_storage_account_name":"testaccount",
                        "azure_blob_storage_container_name":"rejected",
                        $fields
                    }""",
                )
                .toObjectStorageConfig(),
        )

    @Test
    fun `Azure defaults use public endpoint and sync scoped paths`() {
        val config = config(""""shared_access_signature":"test-sas"""")
        assertEquals("AzureBlob", config.type)
        assertEquals("testaccount", config.azureBlobStorageClientConfiguration.accountName)
        assertEquals("rejected", config.azureBlobStorageClientConfiguration.containerName)
        assertEquals("test-sas", config.azureBlobStorageClientConfiguration.sharedAccessSignature)
        assertEquals(
            "blob.core.windows.net",
            config.azureBlobStorageClientConfiguration.endpointDomainName,
        )
        assertInstanceOf(
            CSVFormatConfiguration::class.java,
            config.objectStorageFormatConfiguration,
        )
        assertEquals("", config.objectStoragePathConfiguration.prefix)
        assertEquals(
            "\${SYNC_ID}/\${NAMESPACE}/\${STREAM_NAME}/",
            config.objectStoragePathConfiguration.pathPattern,
        )
        assertEquals(
            "{date}_{timestamp}_{part_number}{format_extension}",
            config.objectStoragePathConfiguration.fileNamePattern,
        )
    }

    @Test
    fun `Azure preserves endpoint prefix path filename and account key`() {
        val config =
            config(
                """"azure_blob_storage_account_key":"test-key",
                "azure_blob_storage_endpoint_domain_name":"blob.core.usgovcloudapi.net",
                "bucket_path":"prefix",
                "format":{"format_type":"JSONL"},
                "path_format":"{sync_id}/{namespace}/{stream_name}",
                "file_name_format":"{part_number}{format_extension}"
            """,
            )
        assertEquals("test-key", config.azureBlobStorageClientConfiguration.accountKey)
        assertInstanceOf(
            JsonFormatConfiguration::class.java,
            config.objectStorageFormatConfiguration,
        )
        assertEquals(
            "blob.core.usgovcloudapi.net",
            config.azureBlobStorageClientConfiguration.endpointDomainName,
        )
        assertEquals("prefix", config.objectStoragePathConfiguration.prefix)
        assertEquals(
            "\${SYNC_ID}/\${NAMESPACE}/\${STREAM_NAME}/",
            config.objectStoragePathConfiguration.pathPattern,
        )
        assertEquals(
            "{part_number}{format_extension}",
            config.objectStoragePathConfiguration.fileNamePattern,
        )
    }

    @Test
    fun `Azure preserves Entra credentials`() {
        val config =
            config(
                """"azure_tenant_id":"test-tenant","azure_client_id":"test-client","azure_client_secret":"test-secret"""",
            )
        assertEquals("test-tenant", config.azureBlobStorageClientConfiguration.tenantId)
        assertEquals("test-client", config.azureBlobStorageClientConfiguration.clientId)
        assertEquals("test-secret", config.azureBlobStorageClientConfiguration.clientSecret)
    }

    @Test
    fun `Azure rejects absent conflicting and incomplete authentication`() {
        listOf(
                """"azure_blob_storage_account_key":"" """,
                """"shared_access_signature":"" """,
                """"shared_access_signature":"test-sas","azure_blob_storage_account_key":"test-key"""",
                """"azure_tenant_id":"test-tenant","azure_client_id":"test-client"""",
            )
            .forEach { fields ->
                val error = assertThrows(IllegalStateException::class.java) { config(fields) }
                assertEquals(
                    "AzureBlobStorageClientConfiguration must have exactly one of: account key, SAS token, or Entra ID authentication (tenant ID, client ID, and client secret)",
                    error.message,
                )
            }
    }

    @Test
    fun `Azure schema preserves contract required fields defaults and hidden formatting`() {
        val schema =
            ValidatedJsonUtils.generateAirbyteJsonSchema(AzureBlobObjectStorageSpec::class.java)
        assertEquals(
            listOf(
                "azure_blob_storage_account_name",
                "azure_blob_storage_container_name",
                "storage_type",
            ),
            schema["required"].map { it.asText() }.sorted(),
        )
        val properties = schema["properties"]
        assertEquals(
            "blob.core.windows.net",
            properties["azure_blob_storage_endpoint_domain_name"]["default"].asText(),
        )
        listOf("format", "path_format", "file_name_format").forEach { field ->
            assertTrue(
                properties[field]["airbyte_hidden"].asBoolean(),
                properties[field].toString(),
            )
        }
        listOf("shared_access_signature", "azure_blob_storage_account_key", "azure_client_secret")
            .forEach { field ->
                assertTrue(
                    properties[field]["airbyte_secret"].asBoolean(),
                    properties[field].toString(),
                )
            }
    }

    @Test
    fun `Azure rejects missing account or container`() {
        listOf("azure_blob_storage_account_name", "azure_blob_storage_container_name").forEach {
            field ->
            val json =
                Jsons.readTree(
                    """{"storage_type":"AzureBlob","azure_blob_storage_account_name":"testaccount","azure_blob_storage_container_name":"rejected","shared_access_signature":"test-sas"}""",
                )
            (json as ObjectNode).remove(field)
            assertThrows(ConfigErrorException::class.java) {
                ValidatedJsonUtils.parseOne(ObjectStorageSpec::class.java, json.toString())
            }
        }
    }
}
