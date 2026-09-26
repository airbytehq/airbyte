/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.DecimalNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import software.amazon.awssdk.core.SdkBytes
import software.amazon.awssdk.services.dynamodb.model.AttributeValue

/**
 * Conversions between DynamoDB [AttributeValue]s and JSON.
 *
 * Two JSON shapes are used:
 * - **record values** ([toRecordValue]): the plain JSON the connector emits in RECORD messages,
 * following the legacy connector's `DynamodbAttributeSerializer` (`S` string, `N` number, `B`
 * base64 string, sets and lists as arrays, `M` as an object, `BOOL`, `NULL`). One deliberate
 * difference: an `N` value that does not fit a `long` is emitted as an exact decimal, where the
 * legacy connector converted it to a lossy `double`;
 * - **DynamoDB JSON** ([toDynamoDbJson], [fromDynamoDbJson]): the typed wire format (`{"S": "x"}`,
 * `{"N": "1"}`, `{"B": "<base64>"}`, ...), which round-trips a value exactly and is used for the
 * key attributes saved in the stream state (`ExclusiveStartKey`).
 */
object DynamoDbJson {

    /**
     * The record value of an attribute, or null for a value type unknown to the SDK (skipped, as
     * the legacy connector did).
     */
    fun toRecordValue(value: AttributeValue): JsonNode? =
        when (value.type()) {
            AttributeValue.Type.S -> Jsons.textNode(value.s())
            AttributeValue.Type.N -> numberNode(value.n())
            AttributeValue.Type.B -> Jsons.binaryNode(value.b().asByteArray())
            AttributeValue.Type.SS ->
                Jsons.arrayNode().apply { value.ss().forEach { add(Jsons.textNode(it)) } }
            AttributeValue.Type.NS ->
                Jsons.arrayNode().apply { value.ns().forEach { add(numberNode(it)) } }
            AttributeValue.Type.BS ->
                Jsons.arrayNode().apply {
                    value.bs().forEach { add(Jsons.binaryNode(it.asByteArray())) }
                }
            AttributeValue.Type.M ->
                Jsons.objectNode().apply {
                    for ((name: String, nested: AttributeValue) in value.m()) {
                        toRecordValue(nested)?.let { set<JsonNode>(name, it) }
                    }
                }
            AttributeValue.Type.L ->
                Jsons.arrayNode().apply {
                    for (element: AttributeValue in value.l()) {
                        toRecordValue(element)?.let { add(it) }
                    }
                }
            AttributeValue.Type.BOOL -> Jsons.booleanNode(value.bool())
            AttributeValue.Type.NUL -> NullNode.instance
            AttributeValue.Type.UNKNOWN_TO_SDK_VERSION,
            null -> null
        }

    /**
     * A DynamoDB number as a JSON number: a `long` when it is one (as the legacy connector did),
     * otherwise the exact decimal the service returned. DynamoDB numbers carry up to 38 digits.
     */
    fun numberNode(n: String): JsonNode {
        n.toLongOrNull()?.let {
            return Jsons.numberNode(it)
        }
        return DecimalNode.valueOf(BigDecimal(n))
    }

    /** The DynamoDB JSON of an attribute value. */
    fun toDynamoDbJson(value: AttributeValue): ObjectNode {
        val node: ObjectNode = Jsons.objectNode()
        when (value.type()) {
            AttributeValue.Type.S -> node.put("S", value.s())
            AttributeValue.Type.N -> node.put("N", value.n())
            AttributeValue.Type.B -> node.put("B", value.b().asByteArray())
            AttributeValue.Type.SS ->
                node.set<JsonNode>("SS", Jsons.arrayNode().apply { value.ss().forEach { add(it) } })
            AttributeValue.Type.NS ->
                node.set<JsonNode>("NS", Jsons.arrayNode().apply { value.ns().forEach { add(it) } })
            AttributeValue.Type.BS ->
                node.set<JsonNode>(
                    "BS",
                    Jsons.arrayNode().apply { value.bs().forEach { add(it.asByteArray()) } },
                )
            AttributeValue.Type.M -> node.set<JsonNode>("M", itemToDynamoDbJson(value.m()))
            AttributeValue.Type.L ->
                node.set<JsonNode>(
                    "L",
                    Jsons.arrayNode().apply { value.l().forEach { add(toDynamoDbJson(it)) } },
                )
            AttributeValue.Type.BOOL -> node.put("BOOL", value.bool())
            AttributeValue.Type.NUL -> node.put("NULL", true)
            AttributeValue.Type.UNKNOWN_TO_SDK_VERSION,
            null -> throw IllegalArgumentException("Unknown DynamoDB attribute value type")
        }
        return node
    }

    /** The DynamoDB JSON of an item or key: attribute name to typed value. */
    fun itemToDynamoDbJson(item: Map<String, AttributeValue>): ObjectNode =
        Jsons.objectNode().apply {
            for ((name: String, value: AttributeValue) in item) {
                set<JsonNode>(name, toDynamoDbJson(value))
            }
        }

    /** Parses an attribute value in DynamoDB JSON (`{"S": "x"}`, `{"N": "1"}`, ...). */
    fun fromDynamoDbJson(node: JsonNode): AttributeValue {
        require(node.isObject && node.size() == 1) {
            "Expected a DynamoDB JSON value with exactly one type key, got $node"
        }
        val (type: String, value: JsonNode) = node.fields().next().let { it.key to it.value }
        val builder: AttributeValue.Builder = AttributeValue.builder()
        when (type) {
            "S" -> builder.s(value.asText())
            "N" -> builder.n(value.asText())
            "B" -> builder.b(SdkBytes.fromByteArray(value.binaryValue()))
            "SS" -> builder.ss(value.map { it.asText() })
            "NS" -> builder.ns(value.map { it.asText() })
            "BS" -> builder.bs(value.map { SdkBytes.fromByteArray(it.binaryValue()) })
            "M" -> builder.m(itemFromDynamoDbJson(value))
            "L" -> builder.l((value as ArrayNode).map(::fromDynamoDbJson))
            "BOOL" -> builder.bool(value.asBoolean())
            "NULL" -> builder.nul(true)
            else -> throw IllegalArgumentException("Unknown DynamoDB JSON type '$type'")
        }
        return builder.build()
    }

    /** Parses an item or key in DynamoDB JSON: attribute name to typed value. */
    fun itemFromDynamoDbJson(node: JsonNode): Map<String, AttributeValue> {
        require(node.isObject) { "Expected a DynamoDB JSON item, got $node" }
        return node.fields().asSequence().associate { (name, value) ->
            name to fromDynamoDbJson(value)
        }
    }
}
