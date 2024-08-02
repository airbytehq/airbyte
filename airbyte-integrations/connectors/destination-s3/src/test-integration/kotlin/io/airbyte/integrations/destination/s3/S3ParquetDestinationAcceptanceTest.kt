/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.s3.S3BaseParquetDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider.Companion.EXCHANGE_RATE_CONFIG
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import org.junit.jupiter.api.Test

class S3ParquetDestinationAcceptanceTest : S3BaseParquetDestinationAcceptanceTest() {
    override fun getProtocolVersion(): ProtocolVersion {
        return ProtocolVersion.V1
    }

    override fun getTestDataComparator(): TestDataComparator {
        return S3AvroParquetTestDataComparator()
    }

    override val baseConfigJson: JsonNode
        get() = S3DestinationTestUtils.baseConfigJsonFilePath

    /**
     * Quick and dirty test to verify that lzo compression works. Probably has some blind spots
     * related to cpu architecture.
     *
     * Only verifies that it runs successfully, which is sufficient to catch any issues with
     * installing the lzo libraries.
     */
    @Test
    @Throws(Exception::class)
    fun testLzoCompression() {
        val config = getConfig().deepCopy<JsonNode>()
        (config["format"] as ObjectNode).put("compression_codec", "LZO")

        val catalog =
            deserialize<AirbyteCatalog>(
                readResource(
                    DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(
                        ProtocolVersion.V0
                    )
                ),
                AirbyteCatalog::class.java
            )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        configuredCatalog.streams.forEach {
            it.withSyncId(42).withGenerationId(12).withMinimumGenerationId(12)
        }
        val messages: List<AirbyteMessage> =
            readResource(
                    DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(
                        ProtocolVersion.V0
                    )
                )
                .lines()
                .filter { it.isNotEmpty() }
                .map { record: String? ->
                    deserialize<AirbyteMessage>(record, AirbyteMessage::class.java)
                }
                .toList()

        runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false)
    }
}
