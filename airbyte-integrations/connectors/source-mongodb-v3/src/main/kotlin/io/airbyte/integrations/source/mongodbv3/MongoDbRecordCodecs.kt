/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons

/**
 * The declared [MongoDbFieldType] of each non-meta field of a stream, keyed by field id. Drives the
 * record converter so protobuf output encodes each value to its declared type.
 */
fun schemaFieldTypesOf(stream: Stream): Map<String, MongoDbFieldType> =
    stream.schema
        .filterNot { it.id.startsWith(MetaField.META_PREFIX) }
        .mapNotNull { field -> (field.type as? MongoDbFieldType)?.let { field.id to it } }
        .toMap()

/**
 * Record-value codecs for the MongoDB source. Each carries a pre-built [JsonNode] straight through
 * on the JSONL channel (`encode`/`decode` are the identity), but converts it to the Java value the
 * schema-driven **protobuf** encoder expects for the field's `airbyteSchemaType` (
 * [valueForProtobufEncoding]).
 *
 * MongoDB is schemaless, so a value's actual BSON type may not match the field's discovered type
 * (the type is only a hint from sampling). On the protobuf channel a value that cannot be coerced
 * to the declared type is emitted as `null` rather than crashing the sync; on the JSONL channel the
 * raw value always flows and the destination coerces it. See `databases/mongodb/README.md`, Stage
 * 4.
 */
sealed class MongoDbValueCodec : ProtobufAwareCustomConnectorJsonCodec<JsonNode> {
    final override fun encode(decoded: JsonNode): JsonNode = decoded

    final override fun decode(encoded: JsonNode): JsonNode = encoded
}

/** For `{"type":"string"}` fields: any non-null value renders as text. */
object MongoStringValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? = if (v.isNull) null else v.asText()
}

/**
 * For `{"type":"number"}` fields: only a JSON number coerces; anything else is nulled on protobuf.
 */
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
 * For `{"type":"object"}` / `{"type":"array"}` (JSONB) fields, and the schemaless `data` field:
 * serialize the node to a JSON string, which the protobuf JSON encoder accepts. Plain string form
 * (not `toString()`) keeps decimals unexponentiated, matching the JSONL channel.
 */
object MongoJsonbValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? =
        if (v.isNull) null else Jsons.writeValueAsString(v)
}

/** For `{"type":"null"}` fields. */
object MongoNullValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: JsonNode): Any? = null
}
