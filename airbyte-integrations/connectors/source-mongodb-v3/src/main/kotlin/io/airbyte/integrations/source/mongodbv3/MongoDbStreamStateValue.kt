/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import java.util.Base64
import org.bson.types.Binary
import org.bson.types.ObjectId

/** Snapshot phase of a collection, matching the legacy connector's `MongoDbStreamState.status`. */
enum class MongoDbSnapshotStatus {
    /** An incremental stream whose initial snapshot is still in progress. */
    IN_PROGRESS,
    /** An incremental stream whose initial snapshot is complete (change stream takes over). */
    COMPLETE,
    /** A full-refresh stream; the snapshot is re-read from the start on every sync. */
    FULL_REFRESH,
}

/**
 * BSON type of a collection's `_id`, matching the legacy connector's `MongoDbStreamState.idType`.
 */
enum class MongoDbIdType {
    OBJECT_ID,
    STRING,
    INT,
    LONG,
    BINARY,
}

/**
 * Per-collection snapshot checkpoint, serialized to the exact JSON shape the legacy
 * `source-mongodb-v2` connector persisted so existing connections keep resuming without a reset:
 * ```
 * {"id": "<last _id>", "status": "IN_PROGRESS|COMPLETE|FULL_REFRESH", "idType": "OBJECT_ID|...",
 *  "binarySubType": 0}
 * ```
 * [id] is the string form of the last emitted `_id`; for a [Binary] `_id` it is the UUID text when
 * the subtype is 4 and Base64 otherwise, as the legacy connector did.
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
            }
        }

    companion object {
        fun fromOpaqueStateValue(state: OpaqueStateValue): MongoDbStreamStateValue =
            Jsons.treeToValue(state, MongoDbStreamStateValue::class.java)

        /** Lenient parse: null for a missing or unparseable state (treated as "no checkpoint"). */
        fun fromOpaqueStateValueOrNull(state: OpaqueStateValue?): MongoDbStreamStateValue? =
            state?.let { runCatching { fromOpaqueStateValue(it) }.getOrNull() }

        /**
         * Builds a checkpoint from the last `_id` value emitted for a collection (null if none).
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
                else -> MongoDbStreamStateValue(lastId?.toString(), status, MongoDbIdType.STRING)
            }

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
