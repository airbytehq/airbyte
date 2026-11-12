/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.integrations.source.mongodb.discover.MongoDbFieldType
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.DATA_FIELD
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import org.bson.BsonDocument
import org.bson.BsonReader
import org.bson.BsonType

/**
 * Builds a [NativeRecordPayload] from a BSON document in one pass over its bytes (see
 * [MongoDbBsonValues] for the value conversions). Every field of [schemaFieldTypes] is emitted —
 * `null` when absent — in its declared type's codec.
 */
class MongoDbRecordConverter(
    private val schemaEnforced: Boolean,
    private val schemaFieldTypes: Map<String, MongoDbFieldType>,
) {

    private val bson = MongoDbBsonValues()

    /** `<field>_aibyte_transform` catalog properties, by the field they stringify. */
    private val transformsBySource: Map<String, String> =
        schemaFieldTypes.keys
            .mapNotNull { name -> transformSourceField(name)?.let { it to name } }
            .toMap()

    /**
     * The document fields a record is built from: the catalog's, and the sources of its
     * `_aibyte_transform` properties.
     */
    val readFields: Set<String> = schemaFieldTypes.keys + transformsBySource.keys

    /**
     * Payload for a change event: the full document for insert/update/replace, or the `{_id}` key
     * plus [deletedAt] (overriding the consumer's null `_ab_cdc_deleted_at`) for a delete.
     */
    fun changePayload(document: BsonDocument, deletedAt: String?): NativeRecordPayload {
        val payload: NativeRecordPayload = toPayload(document)
        if (deletedAt != null) {
            payload[CommonMetaField.CDC_DELETED_AT.id] =
                FieldValueEncoder(MongoDbValue.Text(deletedAt), MongoStringValueCodec)
        }
        return payload
    }

    fun toPayload(document: BsonDocument): NativeRecordPayload =
        if (schemaEnforced) enforcedPayload(document) else schemalessPayload(document)

    /** `_id` plus the whole document under a single `data` field. */
    private fun schemalessPayload(document: BsonDocument): NativeRecordPayload {
        val payload: NativeRecordPayload = HashMap()
        val id: MongoDbValue? = document[ID_FIELD]?.let(bson::valueOf)
        payload[ID_FIELD] = FieldValueEncoder(id, schemaFieldTypes.getValue(ID_FIELD).valueCodec)
        val text: String = document.asBsonReader().use(bson::documentText)
        payload[DATA_FIELD] =
            FieldValueEncoder(MongoDbValue.Json(text, isArray = false), MongoJsonbValueCodec)
        return payload
    }

    /**
     * The catalog's fields in their declared codecs; a `<field>_aibyte_transform` property receives
     * `<field>` JSON-stringified while `<field>` itself is nulled.
     */
    private fun enforcedPayload(document: BsonDocument): NativeRecordPayload {
        val payload: NativeRecordPayload = HashMap()
        document.asBsonReader().use { reader: BsonReader -> readInto(payload, reader) }
        for ((name: String, type: MongoDbFieldType) in schemaFieldTypes) {
            payload.putIfAbsent(name, FieldValueEncoder(null, type.valueCodec))
        }
        return payload
    }

    private fun readInto(payload: NativeRecordPayload, reader: BsonReader) {
        reader.readStartDocument()
        while (true) {
            val bsonType: BsonType = reader.readBsonType()
            if (bsonType == BsonType.END_OF_DOCUMENT) break
            val name: String = reader.readName()
            val type: MongoDbFieldType? = schemaFieldTypes[name]
            val transform: String? = transformsBySource[name]
            if (type == null && transform == null) {
                reader.skipValue()
                continue
            }
            val value: MongoDbValue? = bson.readValue(reader, bsonType)
            if (type != null) {
                payload[name] = FieldValueEncoder(coerceToSchema(value, type), type.valueCodec)
            }
            if (transform != null) {
                payload[transform] =
                    FieldValueEncoder(value?.let(::stringify), MongoStringValueCodec)
                type?.let { payload[name] = FieldValueEncoder(null, it.valueCodec) }
            }
        }
        reader.readEndDocument()
    }

    /**
     * A non-array value in a field declared `array` would become `null` downstream, so a value
     * **present** in the document (a BSON `null` included → `[null]`) is wrapped in a one-element
     * array.
     */
    private fun coerceToSchema(value: MongoDbValue?, type: MongoDbFieldType): MongoDbValue? =
        if (
            type == MongoDbFieldType.ARRAY &&
                value != null &&
                !(value is MongoDbValue.Json && value.isArray)
        ) {
            MongoDbValue.Json("[${value.toJsonText()}]", isArray = true)
        } else {
            value
        }

    /** The text itself for a text value, compact JSON for anything else. */
    private fun stringify(value: MongoDbValue): MongoDbValue =
        if (value is MongoDbValue.Text) value else MongoDbValue.Text(value.toJsonText())

    /**
     * The field a `<field>_aibyte_transform` catalog property derives from, or null. Adding the
     * suffixed `string` property to the catalog yields the field's value JSON-stringified.
     */
    private fun transformSourceField(name: String): String? =
        name.removeSuffix(TRANSFORM_SUFFIX).takeIf { it != name && it.isNotEmpty() }

    companion object {
        /** Catalog marker for "emit this field JSON-stringified" (sic: `aibyte`). */
        const val TRANSFORM_SUFFIX = "_aibyte_transform"
    }
}
