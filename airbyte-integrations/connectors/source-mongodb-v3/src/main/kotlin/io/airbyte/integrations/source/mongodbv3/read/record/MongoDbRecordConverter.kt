/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.record

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
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.SignStyle
import java.time.temporal.ChronoField
import java.util.Base64
import org.bson.BinaryVector
import org.bson.BsonBinary
import org.bson.BsonDbPointer
import org.bson.BsonRegularExpression
import org.bson.BsonUndefined
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
 * Converts a BSON [Document] into a [NativeRecordPayload]: `ObjectId` as hex, `Date` with millis,
 * `Binary` (any subtype) as Base64, regex as `(options)pattern`, `CodeWithScope` as an object;
 * `MinKey`, `MaxKey`, `undefined` and `DBPointer` values are omitted. With [schemaFieldTypes]
 * (READ) every schema field is emitted — `null` when absent — in its declared type's codec; without
 * it, only the document's own fields in a passthrough codec.
 */
class MongoDbRecordConverter(
    private val schemaEnforced: Boolean,
    private val schemaFieldTypes: Map<String, MongoDbFieldType> = emptyMap(),
) {

    /**
     * Payload for a change event: the full document for insert/update/replace, or the `{_id}` key
     * plus [deletedAt] (overriding the consumer's null `_ab_cdc_deleted_at`) for a delete.
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
                        // `<field>_aibyte_transform`: stringified `<field>`, which itself is
                        // nulled.
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
     * A non-array value in a field declared `array` would become `null` downstream, so a value
     * **present** in the document (a BSON `null` included → `[null]`) is wrapped in a one-element
     * array.
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
     * The field a `<field>_aibyte_transform` catalog property derives from, or null. Adding the
     * suffixed `string` property to the catalog yields the field's value JSON-stringified.
     */
    private fun transformSourceField(name: String): String? =
        name.removeSuffix(TRANSFORM_SUFFIX).takeIf { it != name && it.isNotEmpty() }

    /** `asText()` for a text value, compact JSON for anything else. */
    private fun stringify(node: JsonNode): JsonNode =
        Jsons.textNode(if (node.isTextual) node.asText() else node.toString())

    private fun documentToObject(document: Document): ObjectNode {
        val node: ObjectNode = Jsons.objectNode()
        for ((name: String, value: Any?) in document) {
            toJsonNode(value)?.let { node.set<JsonNode>(name, it) }
        }
        return node
    }

    /** The JSON encoding of a BSON value, or `null` for values that are dropped. */
    private fun toJsonNode(value: Any?): JsonNode? =
        when (value) {
            null -> Jsons.nullNode()
            is MinKey,
            is MaxKey,
            is BsonUndefined,
            is BsonDbPointer -> null
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
            is BinaryVector ->
                Jsons.textNode(Base64.getEncoder().encodeToString(BsonBinary(value).data))
            is ByteArray -> Jsons.textNode(Base64.getEncoder().encodeToString(value))
            // `(options)pattern`, or just the pattern when there are no options.
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

    private fun formatDate(date: java.util.Date): String = ISO_MILLIS.format(date.toInstant())

    /** The raw 64-bit `BsonTimestamp` value formatted as if it were epoch millis. */
    private fun formatBsonTimestamp(timestamp: org.bson.BsonTimestamp): String =
        ISO_MILLIS.format(Instant.ofEpochMilli(timestamp.value))

    companion object {
        /** Catalog marker for "emit this field JSON-stringified" (sic: `aibyte`). */
        const val TRANSFORM_SUFFIX = "_aibyte_transform"

        /**
         * `yyyy-MM-dd'T'HH:mm:ss.SSS'Z'` in UTC: milliseconds always present, no sign on a year
         * beyond 9999 (unlike `Instant.toString()`).
         */
        private val ISO_MILLIS: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .appendValue(ChronoField.YEAR, 4, 10, SignStyle.NORMAL)
                .appendPattern("-MM-dd'T'HH:mm:ss.SSS'Z'")
                .toFormatter()
                .withZone(ZoneOffset.UTC)
    }
}
