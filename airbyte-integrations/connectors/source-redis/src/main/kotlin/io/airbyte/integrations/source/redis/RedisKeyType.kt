/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.FieldType

enum class RedisKeyType(
    val streamName: String,
    val fields: List<RedisField>,
    val primaryKey: List<List<String>>,
    val incremental: Boolean = false,
) {
    STRINGS(
        "strings",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("value", RedisFieldType.STRING),
            RedisField("ttl", RedisFieldType.INTEGER)
        ),
        listOf(listOf("key")),
    ),
    HASHES(
        "hashes",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("value", RedisFieldType.JSONB),
            RedisField("ttl", RedisFieldType.INTEGER)
        ),
        listOf(listOf("key")),
    ),
    LISTS(
        "lists",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("value", RedisFieldType.ARRAY_STRING),
            RedisField("ttl", RedisFieldType.INTEGER)
        ),
        listOf(listOf("key")),
    ),
    SETS(
        "sets",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("value", RedisFieldType.ARRAY_STRING),
            RedisField("ttl", RedisFieldType.INTEGER)
        ),
        listOf(listOf("key")),
    ),
    SORTED_SETS(
        "sorted_sets",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("value", RedisFieldType.ARRAY_JSONB),
            RedisField("ttl", RedisFieldType.INTEGER)
        ),
        listOf(listOf("key")),
    ),
    STREAMS(
        "streams",
        listOf(
            RedisField("key", RedisFieldType.STRING),
            RedisField("id", RedisFieldType.STRING),
            RedisField("fields", RedisFieldType.JSONB)
        ),
        listOf(listOf("key"), listOf("id")),
        incremental = true,
    ),
}

data class RedisField(
    val name: String,
    val type: RedisFieldType,
)

enum class RedisFieldType(
    override val airbyteSchemaType: AirbyteSchemaType,
) : FieldType {
    STRING(LeafAirbyteSchemaType.STRING),
    INTEGER(LeafAirbyteSchemaType.INTEGER),
    JSONB(LeafAirbyteSchemaType.JSONB),
    ARRAY_STRING(ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING)),
    ARRAY_JSONB(ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB)),
    ;

    override val jsonEncoder: JsonEncoder<JsonNode> = JsonEncoder { it }
}
