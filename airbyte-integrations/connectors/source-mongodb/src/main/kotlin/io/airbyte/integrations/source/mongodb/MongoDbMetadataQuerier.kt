/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.MongoCommandException
import com.mongodb.client.AggregateIterable
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoCursor
import com.mongodb.client.model.Aggregates
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import org.bson.Document
import java.util.concurrent.TimeUnit

private val log = KotlinLogging.logger {}

/**
 * MongoDB implementation of [MetadataQuerier].
 *
 * This class handles schema discovery for MongoDB collections by:
 * - Listing available collections in the configured database
 * - Sampling documents to infer field schemas
 * - Returning `_id` as the primary key for all collections
 */
class MongoDbMetadataQuerier(
    private val config: MongoDbSourceConfiguration,
    private val mongoClient: MongoClient,
) : MetadataQuerier {

    companion object {
        /** MongoDB's default primary key field. */
        const val ID_FIELD = "_id"

        /** Collection prefixes that should be ignored during discovery. */
        private val IGNORED_COLLECTION_PREFIXES = setOf("system.", "replset.", "oplog.")

        /** Default timeout for discovery queries in seconds. */
        private const val DEFAULT_DISCOVER_TIMEOUT_SECONDS = 600
    }

    /** Cached collection names for the configured database. */
    private val memoizedCollectionNames: Set<String> by lazy {
        getAuthorizedCollections()
    }

    /** Cached field metadata per collection. */
    private val memoizedFieldsByCollection: MutableMap<String, List<Field>> = mutableMapOf()

    override fun streamNamespaces(): List<String> {
        // MongoDB: namespace is the database name
        return listOf(config.database)
    }

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        // Return collections in the configured database
        return memoizedCollectionNames.map { collectionName ->
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName(collectionName)
                    .withNamespace(config.database)
            )
        }
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val collectionName = streamID.name
        if (collectionName !in memoizedCollectionNames) {
            return emptyList()
        }

        return memoizedFieldsByCollection.getOrPut(collectionName) {
            discoverFieldsInCollection(collectionName)
        }
    }

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        // MongoDB always has `_id` as the primary key
        return listOf(listOf(ID_FIELD))
    }

    override fun extraChecks() {
        // Verify we can connect and access the database
        try {
            mongoClient.getDatabase(config.database).runCommand(Document("ping", 1))
            log.info { "Successfully connected to MongoDB database: ${config.database}" }
        } catch (e: Exception) {
            throw io.airbyte.cdk.ConfigErrorException(
                "Failed to connect to MongoDB database '${config.database}': ${e.message}",
                e
            )
        }
    }

    override fun close() {
        mongoClient.close()
    }

    /**
     * Returns the set of collections that the current credentials are authorized to access.
     */
    private fun getAuthorizedCollections(): Set<String> {
        try {
            val document = mongoClient.getDatabase(config.database).runCommand(
                Document("listCollections", 1)
                    .append("authorizedCollections", true)
                    .append("nameOnly", true)
            ).append("filter", "{ 'type': 'collection' }")

            val bsonDocument = document.toBsonDocument()
            val cursor = bsonDocument.get("cursor")?.asDocument()
                ?: return emptySet()
            val firstBatch = cursor.getArray("firstBatch")
                ?: return emptySet()

            return firstBatch
                .asSequence()
                .mapNotNull { it?.asDocument()?.getString("name")?.value }
                .filter { isSupportedCollection(it) }
                .toSet()
        } catch (e: MongoCommandException) {
            log.warn { "Failed to list collections: ${e.message}. Falling back to listCollectionNames." }
            // Fallback to basic collection listing
            return mongoClient.getDatabase(config.database)
                .listCollectionNames()
                .filter { isSupportedCollection(it) }
                .toSet()
        }
    }

    /**
     * Checks if a collection should be included in discovery.
     */
    private fun isSupportedCollection(collectionName: String): Boolean {
        return IGNORED_COLLECTION_PREFIXES.none { collectionName.startsWith(it) }
    }

    /**
     * Discovers fields in a collection by sampling documents.
     *
     * Uses MongoDB's aggregation framework to sample documents and extract
     * field names with their BSON types.
     */
    private fun discoverFieldsInCollection(collectionName: String): List<Field> {
        val discoveredFields = mutableMapOf<String, MongoDbFieldType>()
        val collection: MongoCollection<Document> =
            mongoClient.getDatabase(config.database).getCollection(collectionName)

        // Build aggregation pipeline to sample documents and extract field types
        val fieldsMap = mapOf(
            "input" to mapOf("\$objectToArray" to "\$\$ROOT"),
            "as" to "each",
            "in" to mapOf("k" to "\$\$each.k", "v" to mapOf("\$type" to "\$\$each.v"))
        )

        val mapFunction = Document("\$map", fieldsMap)
        val arrayToObjectAggregation = Document("\$arrayToObject", mapFunction)

        val groupMap = mutableMapOf<String, Any>()
        groupMap["_id"] = "\$fields"

        val aggregateList = listOf(
            Aggregates.sample(config.discoverSampleSize),
            Aggregates.project(Document("fields", arrayToObjectAggregation)),
            Aggregates.unwind("\$fields"),
            Document("\$group", groupMap)
        )

        try {
            val output: AggregateIterable<Document> = collection.aggregate(aggregateList)
            output.allowDiskUse(true)
                .maxTime(DEFAULT_DISCOVER_TIMEOUT_SECONDS.toLong(), TimeUnit.SECONDS)
                .cursor().use { cursor: MongoCursor<Document> ->
                    while (cursor.hasNext()) {
                        @Suppress("UNCHECKED_CAST")
                        val fields = cursor.next().get("_id") as? Map<String, String> ?: continue
                        fields.forEach { (fieldName, bsonType) ->
                            // Keep the most specific type if we've seen this field before
                            val newType = MongoDbFieldType.fromBsonTypeName(bsonType)
                            val existingType = discoveredFields[fieldName]
                            if (existingType == null || shouldReplaceType(existingType, newType)) {
                                discoveredFields[fieldName] = newType
                            }
                        }
                    }
                }
            log.info { "Discovered ${discoveredFields.size} fields in collection: $collectionName" }
        } catch (e: Exception) {
            log.warn { "Error discovering fields for collection $collectionName: ${e.message}" }
            // If discovery fails, at least return the _id field
            if (discoveredFields.isEmpty()) {
                discoveredFields[ID_FIELD] = MongoDbFieldType.OBJECT_ID
            }
        }

        // Ensure _id is always included
        if (ID_FIELD !in discoveredFields) {
            discoveredFields[ID_FIELD] = MongoDbFieldType.OBJECT_ID
        }

        return discoveredFields.map { (name, type) -> Field(name, type) }
    }

    /**
     * Determines if we should replace an existing field type with a new one.
     *
     * Prefers more specific types over generic ones (e.g., INT over STRING).
     */
    private fun shouldReplaceType(existing: MongoDbFieldType, new: MongoDbFieldType): Boolean {
        // If the new type is NULL, don't replace
        if (new == MongoDbFieldType.NULL) return false
        // If the existing type is NULL, replace with the new type
        if (existing == MongoDbFieldType.NULL) return true
        // Otherwise, keep the first non-null type we found
        return false
    }

    /** Factory for creating [MongoDbMetadataQuerier] instances. */
    @Singleton
    class Factory : MetadataQuerier.Factory<MongoDbSourceConfiguration> {
        override fun session(config: MongoDbSourceConfiguration): MetadataQuerier {
            val mongoClient = config.createMongoClient()
            return MongoDbMetadataQuerier(config, mongoClient)
        }
    }
}
