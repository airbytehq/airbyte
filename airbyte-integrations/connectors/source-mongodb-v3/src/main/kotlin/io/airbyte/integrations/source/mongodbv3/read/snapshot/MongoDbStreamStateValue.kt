/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.snapshot

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import java.util.Base64
import org.bson.BsonDocument
import org.bson.Document
import org.bson.json.JsonMode
import org.bson.json.JsonWriterSettings
import org.bson.types.Binary
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
}

/**
 * Per-collection snapshot checkpoint: `{"id": "<last _id>", "status": ..., "idType": ...,
 * "binarySubType": 0}`. [id] is the string form of the last emitted `_id` (UUID text for a
 * subtype-4 [Binary], Base64 for other binaries).
 */
data class MongoDbStreamStateValue(
    @JsonProperty("id") val id: String?,
    @JsonProperty("status") val status: MongoDbSnapshotStatus,
    @JsonProperty("idType") val idType: MongoDbIdType,
    @JsonProperty("binarySubType") val binarySubType: Int = 0,
) {
    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /**
     * The checkpointed `_id` reconstructed as its native BSON type, for a `_id > lastSeen` resume
     * query. Returns null when there is no checkpoint yet (fresh read).
     */
    fun resumeIdValue(): Any? =
        id?.let {
            when (idType) {
                MongoDbIdType.OBJECT_ID -> ObjectId(it)
                MongoDbIdType.INT -> it.toInt()
                MongoDbIdType.LONG -> it.toLong()
                MongoDbIdType.STRING -> it
                MongoDbIdType.BINARY -> reconstructBinary(it, binarySubType)
                MongoDbIdType.OBJECT -> BsonDocument.parse(it)
            }
        }

    companion object {
        fun fromOpaqueStateValue(state: OpaqueStateValue): MongoDbStreamStateValue =
            Jsons.treeToValue(state, MongoDbStreamStateValue::class.java)

        /** Lenient parse: null for a missing or unparseable state (treated as "no checkpoint"). */
        fun fromOpaqueStateValueOrNull(state: OpaqueStateValue?): MongoDbStreamStateValue? =
            state?.let { runCatching { fromOpaqueStateValue(it) }.getOrNull() }

        /**
         * Checkpoint for the last `_id` emitted (null if none). A document `_id` is stored as
         * extended JSON so it round-trips losslessly; other types fall back to `toString()`.
         */
        fun fromLastId(lastId: Any?, status: MongoDbSnapshotStatus): MongoDbStreamStateValue =
            when (lastId) {
                is ObjectId ->
                    MongoDbStreamStateValue(lastId.toHexString(), status, MongoDbIdType.OBJECT_ID)
                is Int -> MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.INT)
                is Long -> MongoDbStreamStateValue(lastId.toString(), status, MongoDbIdType.LONG)
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
                val uuid = java.util.UUID.fromString(id)
                val bytes =
                    java.nio.ByteBuffer.allocate(UUID_BYTE_LENGTH)
                        .putLong(uuid.mostSignificantBits)
                        .putLong(uuid.leastSignificantBits)
                        .array()
                Binary(subType.toByte(), bytes)
            } else {
                Binary(subType.toByte(), Base64.getDecoder().decode(id))
            }

        /** UUID text for the standard-UUID subtype (4), Base64 for any other binary subtype. */
        private fun binaryIdToString(binary: Binary): String =
            if (binary.type.toInt() == UUID_SUBTYPE && binary.data.size == UUID_BYTE_LENGTH) {
                val buffer = java.nio.ByteBuffer.wrap(binary.data)
                java.util.UUID(buffer.long, buffer.long).toString()
            } else {
                Base64.getEncoder().encodeToString(binary.data)
            }

        private const val UUID_SUBTYPE = 4
        private const val UUID_BYTE_LENGTH = 16
    }
}
