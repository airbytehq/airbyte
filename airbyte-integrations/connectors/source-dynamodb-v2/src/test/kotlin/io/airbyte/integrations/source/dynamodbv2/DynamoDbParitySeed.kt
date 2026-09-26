/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.createTableWithItems
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType

/**
 * Loads `parity-seed.json`, the dataset shared with the legacy parity harness (`seed.py` in the
 * `new-database-source-connector` skill), so that `expected-catalog.json`, captured from the legacy
 * image on that data, applies to the Testcontainers tests too.
 *
 * A table entry may carry `generate` instead of / in addition to `items`:
 * - `count` + `itemTemplate` (+ `extraFrom` + `extraTemplate`): `count` items, `i` = 1..count,
 * every string expanded with `{i}` / `{i:04d}`; items with `i >= extraFrom` also get the
 * `extraTemplate` attributes;
 * - `tables`: the table `name` is a template expanded with `{i:03d}` for `i` = 1..tables; every
 * generated table gets the same key schema and the listed items (expanded with the same `i`).
 */
object DynamoDbParitySeed {
    const val RESOURCE = "parity-seed.json"

    data class Table(
        val name: String,
        val keySchema: List<KeyElement>,
        val items: List<Map<String, AttributeValue>>,
    )

    fun tables(): List<Table> {
        val root: JsonNode = Jsons.readTree(ResourceUtils.readResource(RESOURCE))
        return root["tables"].flatMap(::expand)
    }

    fun seed(client: DynamoDbClient) {
        for (table in tables()) {
            client.createTableWithItems(table.name, table.keySchema, table.items)
        }
    }

    private fun expand(entry: JsonNode): List<Table> {
        val keySchema: List<KeyElement> =
            entry["keySchema"].map {
                KeyElement(
                    it["attributeName"].asText(),
                    KeyType.fromValue(it["keyType"].asText()),
                    ScalarAttributeType.fromValue(it["attributeType"].asText()),
                )
            }
        val generate: JsonNode? = entry["generate"]
        val literalItems: List<JsonNode> = entry["items"]?.toList() ?: emptyList()
        if (generate?.has("tables") == true) {
            return (1..generate["tables"].asInt()).map { i: Int ->
                Table(
                    name = expandTemplate(entry["name"].asText(), i),
                    keySchema = keySchema,
                    items = literalItems.map { DynamoDbLocalContainer.item(expandTemplate(it, i)) },
                )
            }
        }
        val items = ArrayList<Map<String, AttributeValue>>()
        literalItems.mapTo(items, DynamoDbLocalContainer::item)
        if (generate?.has("count") == true) {
            val extraFrom: Int = generate["extraFrom"]?.asInt() ?: Int.MAX_VALUE
            for (i in 1..generate["count"].asInt()) {
                val item: ObjectNode = expandTemplate(generate["itemTemplate"], i) as ObjectNode
                if (i >= extraFrom) {
                    item.setAll<ObjectNode>(
                        expandTemplate(generate["extraTemplate"], i) as ObjectNode
                    )
                }
                items.add(DynamoDbLocalContainer.item(item))
            }
        }
        return listOf(Table(entry["name"].asText(), keySchema, items))
    }

    private val PLACEHOLDER = Regex("""\{i(?::0(\d)d)?}""")

    /** Python `str.format` placeholders `{i}` and `{i:0Nd}`. */
    fun expandTemplate(template: String, i: Int): String =
        PLACEHOLDER.replace(template) { match: MatchResult ->
            val width: String? = match.groupValues[1].ifEmpty { null }
            if (width == null) i.toString() else "%0${width}d".format(i)
        }

    private fun expandTemplate(node: JsonNode, i: Int): JsonNode =
        when (node) {
            is TextNode -> TextNode.valueOf(expandTemplate(node.asText(), i))
            is ObjectNode ->
                Jsons.objectNode().also { copy: ObjectNode ->
                    node.fields().forEach { (k, v) -> copy.set<JsonNode>(k, expandTemplate(v, i)) }
                }
            is ArrayNode ->
                Jsons.arrayNode().also { copy -> node.forEach { copy.add(expandTemplate(it, i)) } }
            else -> node
        }
}
