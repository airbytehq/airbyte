/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec

/**
 * Record-value codecs: a [MongoDbValue] goes to the JSON channel as it is, and to the protobuf
 * channel coerced to the Java type the schema-driven encoder expects for the field's
 * `airbyteSchemaType`. A value that cannot be coerced (the discovered type is only a sampling hint)
 * is nulled on protobuf.
 */
sealed class MongoDbValueCodec : ProtobufAwareCustomConnectorJsonCodec<MongoDbValue> {
    final override fun encode(decoded: MongoDbValue): JsonNode = decoded.toJsonNode()

    final override fun decode(encoded: JsonNode): MongoDbValue =
        when {
            encoded.isNull -> MongoDbValue.Null
            encoded.isTextual -> MongoDbValue.Text(encoded.textValue())
            encoded.isBoolean -> MongoDbValue.Bool(encoded.booleanValue())
            encoded.isIntegralNumber -> MongoDbValue.Num(encoded.longValue())
            encoded.isNumber -> MongoDbValue.Num(encoded.decimalValue())
            else -> MongoDbValue.Json(encoded.toString(), encoded.isArray)
        }
}

/** `{"type":"string"}`: any value as text, a document or array as its JSON. */
object MongoStringValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: MongoDbValue): Any? =
        when (v) {
            is MongoDbValue.Null -> null
            is MongoDbValue.Text -> v.value
            else -> v.toJsonText()
        }
}

object MongoNumberValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: MongoDbValue): Any? =
        (v as? MongoDbValue.Num)?.toBigDecimal()
}

object MongoBooleanValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: MongoDbValue): Any? = (v as? MongoDbValue.Bool)?.value
}

/** `{"type":"object"}` / `{"type":"array"}` and the schemaless `data` field: the JSON text. */
object MongoJsonbValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: MongoDbValue): Any? =
        if (v is MongoDbValue.Null) null else v.toJsonText()
}

object MongoNullValueCodec : MongoDbValueCodec() {
    override fun valueForProtobufEncoding(v: MongoDbValue): Any? = null
}
