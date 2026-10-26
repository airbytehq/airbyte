/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.snapshot

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.read.MongoDbStateMigration
import java.util.Base64
import java.util.Date
import java.util.UUID
import org.bson.BsonBinary
import org.bson.BsonDateTime
import org.bson.BsonDecimal128
import org.bson.BsonDocument
import org.bson.BsonDouble
import org.bson.BsonInt32
import org.bson.BsonInt64
import org.bson.BsonNull
import org.bson.BsonObjectId
import org.bson.BsonString
import org.bson.BsonTimestamp
import org.bson.BsonValue
import org.bson.Document
import org.bson.json.JsonMode
import org.bson.json.JsonWriterSettings
import org.bson.types.Binary
import org.bson.types.Decimal128
import org.bson.types.ObjectId

/** Snapshot phase of a collection. */
enum class MongoDbSnapshotStatus {
    /** An incremental stream whose initial snapshot is still in progress. */
    IN_PROGRESS,
    /** An incremental stream whose initial snapshot is complete (change stream takes over). */
    COMPLETE,
    /** A full-refresh stream; the snapshot is re-read from the start on every sync. */
    FULL_REFRESH,
}

/**
 * BSON type of a collection's `_id`; [OBJECT] is an `_id` that is itself a document, [BSON] any
 * other kind (code, symbol, boolean, null, ...), kept typed as the extended JSON of `{"v": <id>}`.
 */
enum class MongoDbIdType {
    OBJECT_ID,
    STRING,
    INT,
    LONG,
    BINARY,
    OBJECT,
    DOUBLE,
    DECIMAL,
    DATE,
    TIMESTAMP,
    BSON,
}

/** BSON type names (`$type` aliases) for grouping `_id` values; all numbers are `number`. */
object MongoDbIdKind {
    fun of(id: Any?): String =
        when (id) {
            null -> "null"
            is Int,
            is Long,
            is Double,
            is Decimal128 -> "number"
            is String -> "string"
            is Document,
            is BsonDocument -> "object"
            is Binary -> "binData"
            is ObjectId -> "objectId"
            is Boolean -> "bool"
            is Date -> "date"
            is BsonTimestamp -> "timestamp"
            else -> id.javaClass.simpleName
        }
}

/**
 * Per-collection snapshot checkpoint `{"id", "status", "idType", "binarySubType"}`; [id] is the
 * last emitted `_id` as text: hex for an ObjectId, UUID for a subtype-4 [Binary] and Base64 for
 * other binaries, extended JSON for a document, epoch milliseconds for a date, the 64-bit value for
 * a timestamp, the number's own text, and the extended JSON of `{"v": <id>}` for any other kind —
 * typed, so the resume filter `_id > <id>` matches the right BSON type (comparison operators only
 * match values of the operand's type).
 */
data class MongoDbStreamStateValue(
    @JsonProperty("id") val id: String?,
    @JsonProperty("status") val status: MongoDbSnapshotStatus,
    @JsonProperty("idType") val idType: MongoDbIdType,
    @JsonProperty("binarySubType") val binarySubType: Int = 0,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** The checkpointed `_id` as its native BSON type for the resume filter; null if none. */
    fun resumeIdValue(): Any? = id?.let {
        when (idType) {
            MongoDbIdType.OBJECT_ID -> ObjectId(it)
            MongoDbIdType.INT -> it.toInt()
            MongoDbIdType.LONG -> it.toLong()
            MongoDbIdType.STRING -> it
            MongoDbIdType.BINARY -> reconstructBinary(it, binarySubType)
            MongoDbIdType.OBJECT -> BsonDocument.parse(it)
            MongoDbIdType.DOUBLE -> it.toDouble()
            MongoDbIdType.DECIMAL -> Decimal128.parse(it)
            MongoDbIdType.DATE -> Date(it.toLong())
            MongoDbIdType.TIMESTAMP -> BsonTimestamp(it.toLong())
            MongoDbIdType.BSON -> BsonDocument.parse(it)[BSON_WRAPPER_FIELD]
        }
    }

    companion object {
        /**
         * A persisted checkpoint; anything else fails the sync rather than restart the snapshot.
         */
        fun fromOpaqueStateValue(state: OpaqueStateValue): MongoDbStreamStateValue =
            try {
                Jsons.treeToValue(state, MongoDbStreamStateValue::class.java)
            } catch (e: Exception) {
                MongoDbStateMigration.failure("stream state $state is not a snapshot checkpoint", e)
            }

        /** The feed's current checkpoint, or null when there is none (absent or empty state). */
        fun fromCurrentState(state: OpaqueStateValue?): MongoDbStreamStateValue? =
            state?.takeUnless { it.isNull || it.isEmpty }?.let(::fromOpaqueStateValue)

        /**
         * Checkpoint for the last `_id` (null if none), as the driver decodes it or as a
         * [BsonValue]; a document `_id` is extended JSON.
         */
        fun fromLastId(lastId: Any?, status: MongoDbSnapshotStatus): MongoDbStreamStateValue =
            when (val id: Any? = if (lastId is BsonValue) javaValue(lastId) else lastId) {
                null -> MongoDbStreamStateValue(null, status, MongoDbIdType.STRING)
                is ObjectId ->
                    MongoDbStreamStateValue(id.toHexString(), status, MongoDbIdType.OBJECT_ID)
                is String -> MongoDbStreamStateValue(id, status, MongoDbIdType.STRING)
                is Int -> MongoDbStreamStateValue(id.toString(), status, MongoDbIdType.INT)
                is Long -> MongoDbStreamStateValue(id.toString(), status, MongoDbIdType.LONG)
                is Double -> MongoDbStreamStateValue(id.toString(), status, MongoDbIdType.DOUBLE)
                is Decimal128 ->
                    MongoDbStreamStateValue(id.toString(), status, MongoDbIdType.DECIMAL)
                is Date -> MongoDbStreamStateValue(id.time.toString(), status, MongoDbIdType.DATE)
                is BsonTimestamp ->
                    MongoDbStreamStateValue(id.value.toString(), status, MongoDbIdType.TIMESTAMP)
                is Binary ->
                    MongoDbStreamStateValue(
                        id = binaryIdToString(id),
                        status = status,
                        idType = MongoDbIdType.BINARY,
                        binarySubType = id.type.toInt(),
                    )
                is BsonDocument ->
                    MongoDbStreamStateValue(id.toJson(EXTENDED_JSON), status, MongoDbIdType.OBJECT)
                else ->
                    MongoDbStreamStateValue(
                        Document(BSON_WRAPPER_FIELD, id).toBsonDocument().toJson(EXTENDED_JSON),
                        status,
                        MongoDbIdType.BSON,
                    )
            }

        /**
         * A raw document's `_id` as the JVM type the resume filter and the checkpoint take; a
         * timestamp or document checkpoints as it is, any other kind through the wrapper.
         */
        private fun javaValue(value: BsonValue): Any? =
            when (value) {
                is BsonNull -> null
                is BsonObjectId -> value.value
                is BsonString -> value.value
                is BsonInt32 -> value.value
                is BsonInt64 -> value.value
                is BsonDouble -> value.value
                is BsonDecimal128 -> value.value
                is BsonDateTime -> Date(value.value)
                is BsonBinary -> Binary(value.type, value.data)
                else -> value
            }

        private const val BSON_WRAPPER_FIELD = "v"

        /** Lossless `_id` document serialization (`{"$numberLong": ...}`, `{"$oid": ...}`, ...). */
        private val EXTENDED_JSON: JsonWriterSettings =
            JsonWriterSettings.builder().outputMode(JsonMode.EXTENDED).build()

        /** Inverse of [binaryIdToString]: rebuilds a [Binary] `_id` from its stored text form. */
        private fun reconstructBinary(id: String, subType: Int): Binary =
            if (subType == UUID_SUBTYPE && UUID_TEXT.matches(id)) {
                BsonBinary(UUID.fromString(id)).let { Binary(it.type, it.data) }
            } else {
                Binary(subType.toByte(), Base64.getDecoder().decode(id))
            }

        /** UUID text for a well-formed standard UUID (subtype 4), Base64 for any other binary. */
        private fun binaryIdToString(binary: Binary): String =
            if (binary.type.toInt() == UUID_SUBTYPE && binary.data.size == UUID_BYTE_LENGTH) {
                BsonBinary(binary.type, binary.data).asUuid().toString()
            } else {
                Base64.getEncoder().encodeToString(binary.data)
            }

        /** `BsonBinarySubType.UUID_STANDARD`. */
        private const val UUID_SUBTYPE = 4
        private const val UUID_BYTE_LENGTH = 16
        /** The text form [binaryIdToString] writes for a 16-byte subtype-4 value; else Base64. */
        private val UUID_TEXT =
            Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    }
}
