/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.read.MongoDbStateMigration
import java.util.Base64
import java.util.Date
import java.util.UUID
import org.bson.BsonBinary
import org.bson.BsonBinarySubType
import org.bson.BsonDocument
import org.bson.BsonTimestamp
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

/** BSON type of a collection's `_id`; [OBJECT] is an `_id` that is itself a document. */
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
 * a timestamp, and the number's own text otherwise.
 */
data class MongoDbStreamStateValue(
    @JsonProperty("id") val id: String?,
    @JsonProperty("status") val status: MongoDbSnapshotStatus,
    @JsonProperty("idType") val idType: MongoDbIdType,
    @JsonProperty("binarySubType") val binarySubType: Int = 0,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** The checkpointed `_id` as its native BSON type for the resume filter; null if none. */
    fun resumeIdValue(): Any? =
        id?.let {
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

        /** Checkpoint for the last `_id` (null if none); a document `_id` is extended JSON. */
        fun fromLastId(lastId: Any?, status: MongoDbSnapshotStatus): MongoDbStreamStateValue =
            when (lastId) {
                is ObjectId ->
                    MongoDbStreamStateValue(lastId.toHexString(), status, MongoDbIdType.OBJECT_ID)
                is Int -> MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.INT)
                is Long -> MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.LONG)
                is Double ->
                    MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.DOUBLE)
                is Decimal128 ->
                    MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.DECIMAL)
                is Date ->
                    MongoDbStreamStateValue(lastId.time.toString(), status, MongoDbIdType.DATE)
                is BsonTimestamp ->
                    MongoDbStreamStateValue(
                        lastId.value.toString(),
                        status,
                        MongoDbIdType.TIMESTAMP
                    )
                is Binary ->
                    MongoDbStreamStateValue(
                        id = binaryIdToString(lastId),
                        status = status,
                        idType = MongoDbIdType.BINARY,
                        binarySubType = lastId.type.toInt(),
                    )
                is Document ->
                    MongoDbStreamStateValue(
                        lastId.toBsonDocument().toJson(EXTENDED_JSON),
                        status,
                        MongoDbIdType.OBJECT,
                    )
                is BsonDocument ->
                    MongoDbStreamStateValue(
                        lastId.toJson(EXTENDED_JSON),
                        status,
                        MongoDbIdType.OBJECT
                    )
                else -> MongoDbStreamStateValue(lastId?.toString(), status, MongoDbIdType.STRING)
            }

        /** Lossless `_id` document serialization (`{"$numberLong": ...}`, `{"$oid": ...}`, ...). */
        private val EXTENDED_JSON: JsonWriterSettings =
            JsonWriterSettings.builder().outputMode(JsonMode.EXTENDED).build()

        /** Inverse of [binaryIdToString]: rebuilds a [Binary] `_id` from its stored text form. */
        private fun reconstructBinary(id: String, subType: Int): Binary =
            if (subType == UUID_SUBTYPE) {
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

        private val UUID_SUBTYPE: Int = BsonBinarySubType.UUID_STANDARD.value.toInt()
        private const val UUID_BYTE_LENGTH = 16
    }
}
