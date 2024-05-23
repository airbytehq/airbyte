/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.mongodb

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.mongodb.ConnectionString
import com.mongodb.MongoConfigurationException
import com.mongodb.ReadConcern
import com.mongodb.client.*
import io.airbyte.cdk.db.AbstractDatabase
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.util.MoreIterators
import java.util.*
import java.util.Spliterators.AbstractSpliterator
import java.util.function.Consumer
import java.util.stream.Stream
import java.util.stream.StreamSupport
import org.bson.BsonDocument
import org.bson.Document
import org.bson.conversions.Bson
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class MongoDatabase(connectionString: String, databaseName: String) :
    AbstractDatabase(), AutoCloseable {
    private val connectionString: ConnectionString
    private val database: com.mongodb.client.MongoDatabase
    private val mongoClient: MongoClient

    init {
        try {
            this.connectionString = ConnectionString(connectionString)
            mongoClient = MongoClients.create(this.connectionString)
            database = mongoClient.getDatabase(databaseName)
        } catch (e: MongoConfigurationException) {
            LOGGER.error(e.message, e)
            throw ConnectionErrorException(e.code.toString(), e.message, e)
        } catch (e: Exception) {
            LOGGER.error(e.message, e)
            throw RuntimeException(e)
        }
    }

    @Throws(Exception::class)
    override fun close() {
        mongoClient.close()
    }

    val databaseNames: MongoIterable<String>
        get() = mongoClient.listDatabaseNames()

    val collectionNames: Set<String?>
        get() {
            val collectionNames = database.listCollectionNames() ?: return Collections.emptySet()
            return MoreIterators.toSet(collectionNames.iterator())
                .filter { c: String -> !c.startsWith(MONGO_RESERVED_COLLECTION_PREFIX) }
                .toSet()
        }

    fun getCollection(collectionName: String): MongoCollection<Document> {
        return database.getCollection(collectionName).withReadConcern(ReadConcern.MAJORITY)
    }

    fun getOrCreateNewCollection(collectionName: String): MongoCollection<Document> {
        val collectionNames = MoreIterators.toSet(database.listCollectionNames().iterator())
        if (!collectionNames.contains(collectionName)) {
            database.createCollection(collectionName)
        }
        return database.getCollection(collectionName)
    }

    @VisibleForTesting
    fun createCollection(name: String): MongoCollection<Document> {
        database.createCollection(name)
        return database.getCollection(name)
    }

    @get:VisibleForTesting
    val name: String
        get() = database.name

    fun read(
        collectionName: String,
        columnNames: List<String>,
        filter: Optional<Bson>
    ): Stream<JsonNode> {
        try {
            val collection = database.getCollection(collectionName)
            val cursor =
                collection.find(filter.orElse(BsonDocument())).batchSize(BATCH_SIZE).cursor()

            return getStream(cursor) { document: Document ->
                    MongoUtils.toJsonNode(document, columnNames)
                }
                .onClose {
                    try {
                        cursor.close()
                    } catch (e: Exception) {
                        throw RuntimeException(e.message, e)
                    }
                }
        } catch (e: Exception) {
            LOGGER.error(
                "Exception attempting to read data from collection: {}, {}",
                collectionName,
                e.message
            )
            throw RuntimeException(e)
        }
    }

    private fun getStream(
        cursor: MongoCursor<Document>,
        mapper: CheckedFunction<Document, JsonNode, Exception>
    ): Stream<JsonNode> {
        return StreamSupport.stream(
            object : AbstractSpliterator<JsonNode>(Long.MAX_VALUE, ORDERED) {
                override fun tryAdvance(action: Consumer<in JsonNode>): Boolean {
                    try {
                        val document = cursor.tryNext() ?: return false
                        action.accept(mapper.apply(document))
                        return true
                    } catch (e: Exception) {
                        throw RuntimeException(e)
                    }
                }
            },
            false
        )
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(MongoDatabase::class.java)
        private const val BATCH_SIZE = 1000
        private const val MONGO_RESERVED_COLLECTION_PREFIX = "system."
    }
}
