/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Projections
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.util.*
import java.util.stream.Collectors
import org.bson.BsonValue
import org.bson.Document
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

@Primary
@Singleton
class MongoDbSourceMetadataQuerier(
    mongoDbClientFactory: MongoDbClientFactory,
    val config: MongoDbSourceConfiguration
) : MetadataQuerier {

    companion object {
        val IGNORED_COLLECTIONS: Set<String> = setOf("system.", "replset.", "oplog.")
        const val ID_FIELD: String = "_id"
    }

    private val mongoClient: MongoClient = mongoDbClientFactory.make(config)

    override fun streamNamespaces(): List<String> {
        return listOf(config.database)
    }

    private fun getAuthorizedCollections(
        mongoClient: MongoClient,
        databaseName: String
    ): Set<String> {
        /*
         * db.runCommand ({listCollections: 1.0, authorizedCollections: true, nameOnly: true }) the command
         * returns only those collections for which the user has privileges. For example, if a user has find
         * action on specific collections, the command returns only those collections; or, if a user has
         * find or any other action, on the database resource, the command lists all collections in the
         * database.
         */
        val document =
            mongoClient
                .getDatabase(databaseName)
                .runCommand(
                    Document("listCollections", 1)
                        .append("authorizedCollections", true)
                        .append("nameOnly", true)
                        .append("filter", Document("type", "collection"))
                )
        var result =
            document
                .toBsonDocument()["cursor"]!!
                .asDocument()
                .getArray("firstBatch")
                .stream()
                .map { bsonValue: BsonValue -> bsonValue.asDocument().getString("name").value }
                .filter { collectionName: String? ->
                    IGNORED_COLLECTIONS.none { ignoredCollectionPrefix: String ->
                        collectionName!!.startsWith(ignoredCollectionPrefix)
                    }
                }
                .collect(Collectors.toSet())

        return result
    }

    @Suppress("UNCHECKED_CAST")
    private fun getFieldsInCollection(
        collection: MongoCollection<Document>,
        sampleSize: Int
    ): List<Field> {
        val fieldsMap =
            mapOf(
                "input" to mapOf("\$objectToArray" to "$\$ROOT"),
                "as" to "each",
                "in" to mapOf("k" to "$\$each.k", "v" to mapOf("\$type" to "$\$each.v")),
            )

        val mapFunction = Document("\$map", fieldsMap)
        val arrayToObjectAggregation = Document("\$arrayToObject", mapFunction)

        val groupMap: MutableMap<String, Any> = mutableMapOf()
        groupMap["_id"] = "\$fields"

        val aggregateList: MutableList<Bson> = ArrayList()
        /*
         * Use sampling to reduce the time it takes to discover fields. Inspired by
         * https://www.mongodb.com/docs/compass/current/sampling/#sampling-method.
         */
        aggregateList.add(Aggregates.sample(sampleSize))
        aggregateList.add(Aggregates.project(Document("fields", arrayToObjectAggregation)))
        aggregateList.add(Aggregates.unwind("\$fields"))
        aggregateList.add(Document("\$group", groupMap))

        /*
         * Runs the following aggregation query: db.<collection name>.aggregate( [ { "$sample": { "size" :
         * 10000 } }, { "$project" : { "fields" : { "$arrayToObject": { "$map" : { "input" : {
         * "$objectToArray" : "$$ROOT" }, "as" : "each", "in" : { "k" : "$$each.k", "v" : { "$type" :
         * "$$each.v" } } } } } } }, { "$unwind" : "$fields" }, { "$group" : { "_id" : $fields } } ] )
         */
        val output = collection.aggregate(aggregateList)
        val discoveredFields: MutableList<Field> = mutableListOf()
        output.allowDiskUse(true).cursor().use { cursor ->
            while (cursor.hasNext()) {
                val fields: Map<String, String>? = cursor.next()["_id"] as Map<String, String>?
                discoveredFields.addAll(
                    fields!!
                        .entries
                        .stream()
                        .map { e: Map.Entry<String, String> ->
                            Field(
                                e.key,
                                convertToFieldType(
                                    e.value,
                                ),
                            )
                        }
                        .collect(Collectors.toList()),
                )
            }
        }
        return discoveredFields
    }

    private fun getFieldsForSchemaless(
        collection: MongoCollection<Document>,
    ): List<Field> {
        val discoveredFields: MutableList<Field> = mutableListOf()

        val output =
            collection.aggregate(
                Arrays.asList<Bson>(
                    Aggregates.sample(1), // Selects one random document
                    Aggregates.project(
                        Projections.fields(
                            Projections.excludeId(), // Excludes the _id field from the result
                            Projections.computed<Document>(
                                "_idType",
                                Document("\$type", "\$_id"),
                            ), // Gets the type of the _id field
                        ),
                    ),
                ),
            )

        output.allowDiskUse(true).cursor().use { cursor ->
            while (cursor.hasNext()) {
                val fieldType: FieldType =
                    convertToFieldType(
                        cursor.next()["_idType"] as String?,
                    )
                discoveredFields.add(Field(ID_FIELD, fieldType))
            }
        }
        return discoveredFields
    }

    private fun convertToFieldType(type: String?): FieldType {
        if (type == null) {
            return MongoNullFieldType
        }
        return when (type) {
            "boolean" -> MongoBooleanFieldType
            "int",
            "long",
            "double",
            "decimal" -> MongoNumberFieldType
            "array" -> MongoObjectFieldType // todo: verify this.
            "object",
            "javascriptWithScope" -> MongoObjectFieldType // todo: verify this.
            "null" -> MongoNullFieldType
            else -> MongoStringFieldType
        }
    }

    /** Returns all available stream names in the given namespace. */
    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        if (streamNamespace == null) {
            return emptyList()
        }
        val collections = getAuthorizedCollections(mongoClient, config.database)

        return collections
            .stream()
            .map { StreamDescriptor().withName(it).withNamespace(streamNamespace) }
            .map { StreamIdentifier.from(it) }
            .collect(Collectors.toList())
    }

    /** Returns all available fields in the given stream. */
    override fun fields(streamID: StreamIdentifier): List<Field> {

        /*
         * Fetch the keys/types from the first N documents and the last N documents from the collection.
         * This is an attempt to "survey" the documents in the collection for variance in the schema keys.
         */
        val mongoCollection: MongoCollection<Document> =
            mongoClient.getDatabase(streamID.namespace!!).getCollection(streamID.name)

        if (config.schemaEnforced) {
            return getFieldsInCollection(
                mongoCollection,
                config.discoverSampleSize,
            )
        } else {
            // In schemaless mode, we only sample one record as we're only interested in the _id
            // field (which
            // exists on every record).
            return getFieldsForSchemaless(
                mongoCollection,
            )
        }
    }

    /** Returns the primary key for the given stream, if it exists; empty list otherwise. */
    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> {
        // not applicable for mongodb
        return listOf()
    }

    /** Executes extra checks which throw a [io.airbyte.cdk.ConfigErrorException] on failure. */
    override fun extraChecks() {
        // todo: add cdc things
        return Unit
    }

    override fun close() {
        mongoClient.close()
    }
}

/** MongoDB implementation of [MetadataQuerier.Factory]. */
@Singleton
@Primary
class Factory(
    val mongoDbClientFactory: MongoDbClientFactory,
) : MetadataQuerier.Factory<MongoDbSourceConfiguration> {
    /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
    override fun session(config: MongoDbSourceConfiguration): MetadataQuerier {
        return MongoDbSourceMetadataQuerier(mongoDbClientFactory, config)
    }
}
