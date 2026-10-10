/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteCatalog
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Runs DISCOVER against a seeded DynamoDB Local container and compares the catalog with the one the
 * legacy `airbyte/source-dynamodb` image produced for the same data (`expected-catalog.json`).
 *
 * Known deviation (2026-09-24): the schemas are written in the canonical Bulk CDK shapes, without
 * `null` in `type` and with integers as `{"type": "number", "airbyte_type": "integer"}`, where the
 * legacy connector wrote `{"type": ["null", "string"]}` and `{"type": ["null", "integer"]}`; the
 * legacy catalog is transformed with [canonical] before comparing, so that everything else (the
 * streams, the attributes, their types, nesting, keys and sync modes) is still asserted identical.
 *
 * The seed (`parity-seed.json`) covers every attribute type, nested maps and lists, a composite
 * key, numeric and binary keys, reserved attribute names, an empty table, a table with more items
 * than the 1000-item sample, and 105 tiny tables to exercise `ListTables` pagination.
 */
class DynamoDbSourceDiscoverTest {

    @Test
    fun testDiscoverMatchesLegacyCatalog() {
        assertCatalogMatchesLegacy(container.config())
    }

    /** DynamoDB Local does not enforce IAM, so the flag must simply not change the catalog. */
    @Test
    fun testDiscoverWithIgnoreMissingReadPermissions() {
        assertCatalogMatchesLegacy(
            container.config(extra = mapOf("ignore_missing_read_permissions_tables" to true)),
        )
    }

    /**
     * With a sample of one item only the attributes of the first scanned item are discovered. On
     * DynamoDB Local the `all_types` items are scanned in the order 1, 3, 2 (partition key hash
     * order, see the parity harness), so item 1's attributes win and item 2's are missing.
     */
    @Test
    fun testDiscoverSampleSizeLimitsTheSample() {
        val catalogs: List<AirbyteCatalog> =
            CliRunner.source(
                    "discover",
                    container.config(extra = mapOf("discover_sample_size" to 1))
                )
                .run()
                .catalogs()
        val allTypes: JsonNode =
            Jsons.valueToTree<JsonNode>(catalogs.single()).get("streams").first {
                it["name"].asText() == "all_types"
            }
        val properties: JsonNode = allTypes["json_schema"]["properties"]
        Assertions.assertTrue(properties.has("str"), properties.toString())
        Assertions.assertFalse(properties.has("only_in_2"), properties.toString())
        Assertions.assertFalse(properties.has("only_in_2_num"), properties.toString())
        // Item 1 holds `flexible` as a string; with the full sample item 2's number wins.
        Assertions.assertEquals(Jsons.textNode("string"), properties["flexible"]["type"])
        // The full sample (default 1000) still yields the legacy catalog.
        assertCatalogMatchesLegacy(container.config(extra = mapOf("discover_sample_size" to 1000)))
    }

    /**
     * A table without items is discovered with its key attributes, typed from `DescribeTable`; the
     * legacy catalog lists it with no properties at all (and the legacy connector could not sync
     * it).
     */
    @Test
    fun testEmptyTableIsDiscoveredWithItsKeyAttributes() {
        val catalogs: List<AirbyteCatalog> =
            CliRunner.source("discover", container.config()).run().catalogs()
        val stream: JsonNode =
            Jsons.valueToTree<JsonNode>(catalogs.single()).get("streams").first {
                it["name"].asText() == EMPTY_TABLE
            }
        Assertions.assertEquals(
            Jsons.readTree("""{"id":{"type":"string"}}"""),
            stream["json_schema"]["properties"],
        )
        Assertions.assertEquals(
            Jsons.readTree("""[["id"]]"""),
            stream["source_defined_primary_key"],
        )
        Assertions.assertEquals(
            Jsons.readTree("""["full_refresh","incremental"]"""),
            stream["supported_sync_modes"],
        )
    }

    /** The fallback types composite, numeric and binary keys from the table description alone. */
    @Test
    fun testKeyAttributeFieldsFollowTheKeySchema() {
        container.client().use { client ->
            val querier =
                DynamoDbSourceMetadataQuerier(
                    DynamoDbSourceConfigurationFactory().make(container.config()),
                    client,
                )
            fun keys(table: String): List<Pair<String, AirbyteSchemaType>> =
                querier.keyAttributeFields(table).map { it.id to it.type.airbyteSchemaType }
            Assertions.assertEquals(
                listOf("pk" to LeafAirbyteSchemaType.STRING, "sk" to LeafAirbyteSchemaType.NUMBER),
                keys("composite_key"),
            )
            Assertions.assertEquals(
                listOf("id" to LeafAirbyteSchemaType.NUMBER),
                keys("numeric_key")
            )
            Assertions.assertEquals(
                listOf("id" to LeafAirbyteSchemaType.BINARY),
                keys("binary_key")
            )
            Assertions.assertEquals(listOf("id" to LeafAirbyteSchemaType.STRING), keys(EMPTY_TABLE))
        }
    }

    private fun assertCatalogMatchesLegacy(config: DynamoDbSourceConfigurationSpecification) {
        val expected: JsonNode =
            normalize(Jsons.readTree(ResourceUtils.readResource(EXPECTED_CATALOG_RESOURCE)))
        val catalogs: List<AirbyteCatalog> = CliRunner.source("discover", config).run().catalogs()
        Assertions.assertEquals(1, catalogs.size)
        val actual: JsonNode = normalize(Jsons.valueToTree(catalogs.first()))
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual),
        )
    }

    /**
     * Stream order is not significant and neither is JSON object key order, which [JsonNode.equals]
     * already ignores.
     *
     * Known deviation: the legacy connector lists an empty table as a stream with no properties,
     * whereas this connector lists its key attributes (
     * [testEmptyTableIsDiscoveredWithItsKeyAttributes]); that stream is removed from both sides
     * before comparing.
     */
    private fun normalize(catalog: JsonNode): JsonNode {
        val streams: ArrayNode = catalog["streams"] as ArrayNode
        val sorted: List<JsonNode> =
            streams
                .filter { it["name"].asText() != EMPTY_TABLE }
                .sortedBy { "${it["namespace"]?.asText() ?: ""}.${it["name"].asText()}" }
                .map { stream: JsonNode ->
                    (stream.deepCopy<ObjectNode>()).apply {
                        set<JsonNode>("json_schema", canonical(stream["json_schema"]))
                    }
                }
        return (catalog.deepCopy<ObjectNode>()).apply {
            set<JsonNode>("streams", Jsons.arrayNode().addAll(sorted))
        }
    }

    /**
     * The legacy schema shapes rewritten as the canonical ones this connector emits: `"null"` is
     * dropped from a `type` array, a lone `integer` becomes `number` + `airbyte_type: integer`,
     * recursively through `properties`, `items` and `anyOf`. Idempotent on a canonical schema, so
     * it is applied to both sides.
     */
    private fun canonical(schema: JsonNode): JsonNode {
        if (!schema.isObject) return schema
        val result: ObjectNode = Jsons.objectNode()
        for ((key: String, value: JsonNode) in schema.properties()) {
            when (key) {
                "type" -> {
                    val type: String =
                        if (value.isArray) {
                            value.map { it.asText() }.filter { it != "null" }.singleOrNull()
                                ?: "null"
                        } else {
                            value.asText()
                        }
                    if (type == "integer") {
                        result.put("type", "number").put("airbyte_type", "integer")
                    } else {
                        result.put("type", type)
                    }
                }
                "properties" -> {
                    val properties: ObjectNode = Jsons.objectNode()
                    for ((name: String, property: JsonNode) in value.properties()) {
                        properties.set<JsonNode>(name, canonical(property))
                    }
                    result.set<JsonNode>(key, properties)
                }
                "items" -> result.set<JsonNode>(key, canonical(value))
                "anyOf" ->
                    result.set<JsonNode>(
                        key,
                        Jsons.arrayNode().apply { value.forEach { add(canonical(it)) } },
                    )
                else -> result.set<JsonNode>(key, value)
            }
        }
        return result
    }

    companion object {
        const val EXPECTED_CATALOG_RESOURCE = "expected-catalog.json"
        const val EMPTY_TABLE = "empty_table"

        lateinit var container: DynamoDbLocalContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            container = DynamoDbLocalContainer().also { it.start() }
            container.client().use(DynamoDbParitySeed::seed)
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            container.stop()
        }
    }
}
