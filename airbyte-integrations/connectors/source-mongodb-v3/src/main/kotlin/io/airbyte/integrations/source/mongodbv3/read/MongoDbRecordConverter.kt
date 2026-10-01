/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbFieldType
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.DATA_FIELD
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import java.time.Instant
import java.util.Base64
import org.bson.BsonRegularExpression
import org.bson.Document
import org.bson.types.Binary
import org.bson.types.Code
import org.bson.types.CodeWithScope
import org.bson.types.Decimal128
import org.bson.types.MaxKey
import org.bson.types.MinKey
import org.bson.types.ObjectId
import org.bson.types.Symbol

/**
 * Converts a BSON [Document] into a [NativeRecordPayload] (`fieldName -> encoder`) that the CDK's
 * record consumer serializes to JSONL or protobuf.
 *
 * The per-type conversions reproduce the legacy `source-mongodb-v2` record shape (see
 * `databases/mongodb/README.md`, Stage 4): `ObjectId` as hex, `Date` always with milliseconds,
 * `Binary` as Base64, `BsonRegularExpression` as `(options)pattern`, `CodeWithScope` as an object,
 * `MinKey`/`MaxKey` omitted, etc.
 *
 * When [schemaFieldTypes] is provided (the READ path), the payload carries **every** schema field —
 * `null` for those absent from the document — each wrapped in the codec matching its declared type,
 * so protobuf output over the socket channel encodes each value to the right type. When it is empty
 * (unit tests) only the document's own fields are emitted, wrapped in a passthrough codec.
 */
class MongoDbRecordConverter(
    private val schemaEnforced: Boolean,
    private val schemaFieldTypes: Map<String, MongoDbFieldType> = emptyMap(),
) {

    /**
     * Builds a payload for a change-stream event. For inserts/updates/replaces [document] is the
     * full document and [deletedAt] is null; for deletes [document] is the `{_id}` key and
     * [deletedAt] is the change's cluster time, which overrides the `_ab_cdc_deleted_at` the record
     * consumer would otherwise set to null.
     */
    fun changePayload(document: Document, deletedAt: String?): NativeRecordPayload {
        val payload: NativeRecordPayload = toPayloadWithId(document).first
        if (deletedAt != null) {
            payload[CommonMetaField.CDC_DELETED_AT.id] =
                FieldValueEncoder(Jsons.textNode(deletedAt), MongoStringValueCodec)
        }
        return payload
    }

    /** Converts a document to a payload, returning the raw `_id` value for state checkpointing. */
    fun toPayloadWithId(document: Document): Pair<NativeRecordPayload, Any?> {
        val rawId: Any? = document[ID_FIELD]
        val payload: NativeRecordPayload = mutableMapOf()
        when {
            !schemaEnforced -> {
                // Schemaless mode emits `_id` plus the whole document under a single `data` field.
                val idCodec: MongoDbValueCodec =
                    schemaFieldTypes[ID_FIELD]?.valueCodec ?: MongoStringValueCodec
                payload[ID_FIELD] = FieldValueEncoder(toJsonNode(rawId), idCodec)
                payload[DATA_FIELD] =
                    FieldValueEncoder(documentToObject(document), MongoJsonbValueCodec)
            }
            schemaFieldTypes.isEmpty() -> {
                // No schema (unit tests): emit only the document's own fields, passthrough codec.
                for ((name: String, value: Any?) in document) {
                    val node: JsonNode = toJsonNode(value) ?: continue
                    payload[name] = FieldValueEncoder(node, MongoJsonbValueCodec)
                }
            }
            else -> {
                // READ path: emit every schema field (null when absent) with its typed codec.
                for ((name: String, type: MongoDbFieldType) in schemaFieldTypes) {
                    val base: String? = transformSourceField(name)
                    if (base != null) {
                        // `<field>_aibyte_transform`: the stringified value of `<field>`, which
                        // itself is nulled (v2's transformToStringIfMarked removed it).
                        val value: JsonNode? =
                            if (document.containsKey(base)) toJsonNode(document[base]) else null
                        payload[name] =
                            FieldValueEncoder(value?.let(::stringify), MongoStringValueCodec)
                        if (base in schemaFieldTypes) {
                            payload[base] =
                                FieldValueEncoder(null, schemaFieldTypes[base]!!.valueCodec)
                        }
                        continue
                    }
                    if (name in payload) continue // nulled by a transform above
                    val present: Boolean = document.containsKey(name)
                    val node: JsonNode? = if (present) toJsonNode(document[name]) else null
                    payload[name] =
                        FieldValueEncoder(coerceToSchema(node, present, type), type.valueCodec)
                }
            }
        }
        return payload to rawId
    }

    /**
     * MongoDB types are dynamic, so a value's shape may not match the field's discovered type.
     * Destinations coerce primitives themselves, but a structural mismatch — a non-array value in a
     * field the catalog declares as `array` — would become `null` downstream. Like v2, wrap any
     * value **present** in the document (a BSON `null` included, giving `[null]`) in a one-element
     * array; a field absent from the document stays `null`. Other mismatches are left to the
     * destination (and, on the protobuf channel, to the per-type codec).
     */
    private fun coerceToSchema(
        node: JsonNode?,
        present: Boolean,
        type: MongoDbFieldType
    ): JsonNode? =
        if (type == MongoDbFieldType.ARRAY && present && node != null && !node.isArray) {
            Jsons.arrayNode().add(node)
        } else {
            node
        }

    /**
     * The field a `<field>_aibyte_transform` catalog property derives from, or null if [name] is
     * not such a property. v2's escape hatch for destinations that cannot take a field's native
     * type: a user adds the suffixed property (type `string`) to the catalog and the connector
     * emits the field's value JSON-stringified under it. Discovery never emits these; they are
     * user-added.
     */
    private fun transformSourceField(name: String): String? =
        name.removeSuffix(TRANSFORM_SUFFIX).takeIf { it != name && it.isNotEmpty() }

    /** v2: `asText()` for a text value, compact JSON for anything else. */
    private fun stringify(node: JsonNode): JsonNode =
        Jsons.textNode(if (node.isTextual) node.asText() else node.toString())

    private fun documentToObject(document: Document): ObjectNode {
        val node: ObjectNode = Jsons.objectNode()
        for ((name: String, value: Any?) in document) {
            toJsonNode(value)?.let { node.set<JsonNode>(name, it) }
        }
        return node
    }

    /**
     * Returns the JSON encoding of a BSON value, or `null` for values the legacy connector drops.
     */
    private fun toJsonNode(value: Any?): JsonNode? =
        when (value) {
            null -> Jsons.nullNode()
            is MinKey,
            is MaxKey -> null
            is ObjectId -> Jsons.textNode(value.toHexString())
            is String -> Jsons.textNode(value)
            is Boolean -> Jsons.booleanNode(value)
            is Int -> Jsons.numberNode(value)
            is Long -> Jsons.numberNode(value)
            is Double -> Jsons.numberNode(value)
            is Decimal128 -> Jsons.numberNode(value.bigDecimalValue())
            is java.util.Date -> Jsons.textNode(formatDate(value))
            is org.bson.BsonTimestamp -> Jsons.textNode(formatBsonTimestamp(value))
            is Binary -> Jsons.textNode(Base64.getEncoder().encodeToString(value.data))
            is ByteArray -> Jsons.textNode(Base64.getEncoder().encodeToString(value))
            // `(options)pattern`, or just the pattern when there are no options, as in v2.
            is BsonRegularExpression ->
                Jsons.textNode(
                    if (value.options.isNullOrBlank()) value.pattern
                    else "(${value.options})${value.pattern}"
                )
            is CodeWithScope ->
                Jsons.objectNode().apply {
                    put("code", value.code)
                    set<JsonNode>("scope", documentToObject(value.scope))
                }
            is Code -> Jsons.textNode(value.code)
            is Symbol -> Jsons.textNode(value.symbol)
            is Document -> documentToObject(value)
            is List<*> ->
                Jsons.arrayNode().apply {
                    for (element: Any? in value) {
                        add(toJsonNode(element) ?: Jsons.nullNode())
                    }
                }
            else -> Jsons.textNode(value.toString())
        }

    /**
     * `Instant.toString()` drops trailing zero milliseconds; the legacy connector always kept them.
     */
    private fun formatDate(date: java.util.Date): String {
        val instant: Instant = date.toInstant()
        val millis: Int = (instant.toEpochMilli() % 1000L).toInt()
        val secondsPart: String = Instant.ofEpochSecond(instant.epochSecond).toString().dropLast(1)
        return "%s.%03dZ".format(secondsPart, if (millis < 0) millis + 1000 else millis)
    }

    /**
     * Reproduces the legacy connector's quirk of formatting a `BsonTimestamp`'s raw 64-bit value as
     * if it were epoch milliseconds. This is a known bug kept for record parity.
     */
    private fun formatBsonTimestamp(timestamp: org.bson.BsonTimestamp): String =
        Instant.ofEpochMilli(timestamp.value).toString()

    companion object {
        /** v2's catalog marker for "emit this field JSON-stringified" (sic: `aibyte`). */
        const val TRANSFORM_SUFFIX = "_aibyte_transform"
    }
}
