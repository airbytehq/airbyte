/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.snapshot

import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Projections
import com.mongodb.client.model.Sorts
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import org.bson.BsonDocument
import org.bson.BsonType
import org.bson.conversions.Bson

/**
 * The BSON types present in a collection's `_id`s, found as the legacy connector found them: the
 * mandatory `_id` index orders values by type bracket before value, so the smallest and the largest
 * `_id` (two covered seeks) pin a single type when they share a one-type bracket; otherwise each
 * candidate type is probed with one index-bounded `$type` query. Numbers of any width are one type,
 * `number`, as they are for the resume comparison (`{_id: {$gt: x}}` brackets them together).
 *
 * A collection mixing types reads whole in an uncut round but, resumed after a checkpoint, reads
 * the checkpointed type only: the legacy connector warned and emitted [ANALYTICS_KEY], and so does
 * this one.
 */
object MongoDbIdTypes {
    /** The analytics trace the legacy connector emitted for a collection mixing `_id` types. */
    const val ANALYTICS_KEY = "db-sources-mongo-multiple-id-types"

    /** `$type` aliases that compare together, in the `_id` index order. */
    private val TYPE_BRACKETS: List<List<String>> =
        listOf(
            listOf("minKey"),
            listOf("null", "undefined"),
            listOf("number"),
            listOf("string", "symbol"),
            listOf("object"),
            listOf("array"),
            listOf("binData"),
            listOf("objectId"),
            listOf("bool"),
            listOf("date"),
            listOf("timestamp"),
            listOf("regex"),
            listOf("javascript", "javascriptWithScope"),
            listOf("dbPointer"),
            listOf("maxKey"),
        )

    /** The `$type` aliases present in [collection]'s `_id`s; empty for an empty collection. */
    fun present(collection: MongoCollection<*>): List<String> {
        val index: MongoCollection<BsonDocument> =
            collection.withDocumentClass(BsonDocument::class.java)
        val minType: BsonType = endpointType(index, Sorts.ascending(ID_FIELD)) ?: return emptyList()
        val maxType: BsonType =
            endpointType(index, Sorts.descending(ID_FIELD)) ?: return emptyList()
        val minBracket: List<String> = bracketOf(minType)
        val maxBracket: List<String> = bracketOf(maxType)
        if (minBracket == maxBracket) {
            if (minBracket.size == 1) return minBracket
            // Types within one bracket interleave in the index: probe each member.
            return minBracket.filter { idOfTypeExists(index, it) }
        }
        // The `_id`s span several brackets: probe every type with one index seek each.
        return (TYPE_BRACKETS.flatten() + alias(minType) + alias(maxType)).distinct().filter {
            idOfTypeExists(index, it)
        }
    }

    /** The type of the first `_id` in [sort] order, or null for an empty collection. */
    private fun endpointType(index: MongoCollection<BsonDocument>, sort: Bson): BsonType? =
        index
            .find()
            .projection(Projections.include(ID_FIELD))
            .sort(sort)
            .limit(1)
            .first()
            ?.get(ID_FIELD)
            ?.bsonType

    /** `$type` predicates get tight index bounds, so this is one seek on the `_id` index. */
    private fun idOfTypeExists(index: MongoCollection<BsonDocument>, typeAlias: String): Boolean =
        index
            .find(Filters.type(ID_FIELD, typeAlias))
            .projection(Projections.include(ID_FIELD))
            .limit(1)
            .first() != null

    private fun bracketOf(type: BsonType): List<String> {
        val alias: String = alias(type)
        return TYPE_BRACKETS.firstOrNull { alias in it } ?: listOf(alias)
    }

    /** The `$type` alias of a driver [BsonType]; every numeric width is `number`. */
    private fun alias(type: BsonType): String =
        when (type) {
            BsonType.INT32,
            BsonType.INT64,
            BsonType.DOUBLE,
            BsonType.DECIMAL128 -> "number"
            BsonType.STRING -> "string"
            BsonType.DOCUMENT -> "object"
            BsonType.ARRAY -> "array"
            BsonType.BINARY -> "binData"
            BsonType.UNDEFINED -> "undefined"
            BsonType.OBJECT_ID -> "objectId"
            BsonType.BOOLEAN -> "bool"
            BsonType.DATE_TIME -> "date"
            BsonType.NULL -> "null"
            BsonType.REGULAR_EXPRESSION -> "regex"
            BsonType.DB_POINTER -> "dbPointer"
            BsonType.JAVASCRIPT -> "javascript"
            BsonType.SYMBOL -> "symbol"
            BsonType.JAVASCRIPT_WITH_SCOPE -> "javascriptWithScope"
            BsonType.TIMESTAMP -> "timestamp"
            BsonType.MIN_KEY -> "minKey"
            BsonType.MAX_KEY -> "maxKey"
            else -> type.name
        }
}
