/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.record

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbFieldType

/** The declared [MongoDbFieldType] of each non-meta field of a stream, by field id. */
fun schemaFieldTypesOf(stream: Stream): Map<String, MongoDbFieldType> =
    stream.schema
        .filterNot { it.id.startsWith(MetaField.META_PREFIX) }
        .mapNotNull { field -> (field.type as? MongoDbFieldType)?.let { field.id to it } }
        .toMap()

/**
 * Record-value codecs: pass a pre-built [JsonNode] through on the JSONL channel, but coerce it to
 * the Java type the schema-driven protobuf encoder expects for the field's `airbyteSchemaType`. A
 * value that cannot be coerced (the discovered type is only a sampling hint) is nulled on protobuf.
 */
sealed class MongoDbValueCodec : ProtobufAwareCustomConnectorJsonCodec<JsonNode> {
    final override fun encode(decoded: JsonNode): JsonNode = decoded

    final override fun decode(encoded: JsonNode): JsonNode = encoded
}

/** For `{"type":"string"}` fields: any non-null value renders as text. */
object MongoStringValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? = if (v.isNull) null else v.asText()
}

/** `{"type":"number"}`: only a JSON number coerces; anything else is nulled on protobuf. */
object MongoNumberValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? =
        if (v.isNumber) v.decimalValue() else null
}

/** For `{"type":"boolean"}` fields. */
object MongoBooleanValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? =
        if (v.isBoolean) v.booleanValue() else null
}

/**
 * `{"type":"object"}` / `{"type":"array"}` and the schemaless `data` field: serialize to a JSON
 * string (via `Jsons`, which keeps decimals unexponentiated like the JSONL channel).
 */
object MongoJsonbValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? =
        if (v.isNull) null else Jsons.writeValueAsString(v)
}

/** For `{"type":"null"}` fields. */
object MongoNullValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? = null
}
