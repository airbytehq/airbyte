/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteCatalog
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Runs DISCOVER against the seeded emulator and compares the catalog with the reviewed snapshots in
 * `expected-catalog-*.json`. The whole-project catalog is compared on the fixture's datasets only:
 * other test classes seed datasets of their own in the shared emulator, and may be running at the
 * same time.
 */
class BigQuerySourceDiscoverTest {

    @Test
    fun testDiscoverSingleDataset() {
        assertCatalogMatches(
            BigQueryEmulatorTestFixture.config(datasetId = BigQueryEmulatorTestFixture.DATASET),
            "expected-catalog-single-dataset.json",
        )
    }

    @Test
    fun testDiscoverAllDatasets() {
        assertCatalogMatches(
            BigQueryEmulatorTestFixture.config(),
            "expected-catalog-all-datasets.json",
            namespaces = BigQueryEmulatorTestFixture.DATASETS,
        )
    }

    /**
     * Compares the discovered catalog with the snapshot; with [namespaces], only the actual streams
     * of those namespaces take part in the comparison.
     */
    private fun assertCatalogMatches(
        config: BigQuerySourceConfigurationSpecification,
        expectedCatalogResource: String,
        namespaces: Set<String>? = null,
    ) {
        val expected: JsonNode =
            normalize(Jsons.readTree(ResourceUtils.readResource(expectedCatalogResource)))
        val catalogs: List<AirbyteCatalog> = CliRunner.source("discover", config).run().catalogs()
        Assertions.assertEquals(1, catalogs.size)
        val actual: JsonNode = normalize(Jsons.valueToTree(catalogs.first()), namespaces)
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual),
        )
    }

    /** Stream order is not significant; JSON object key order is ignored by [JsonNode.equals]. */
    private fun normalize(catalog: JsonNode, namespaces: Set<String>? = null): JsonNode {
        val streams: ArrayNode = catalog["streams"] as ArrayNode
        val sorted: List<JsonNode> =
            streams
                .filter { namespaces == null || it["namespace"].asText() in namespaces }
                .sortedBy { "${it["namespace"].asText()}.${it["name"].asText()}" }
        return (catalog.deepCopy<ObjectNode>()).apply {
            set<JsonNode>("streams", Jsons.arrayNode().addAll(sorted))
        }
    }

    companion object {
        @JvmStatic
        @BeforeAll
        fun startEmulator() {
            BigQueryEmulatorTestFixture.start()
        }
    }
}
