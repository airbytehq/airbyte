/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Projections
import com.mongodb.connection.ClusterType
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.Callable
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ExecutionException
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit
import org.bson.BsonDocument
import org.bson.Document
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/**
 * MongoDB implementation of [MetadataQuerier].
 *
 * Namespaces are the configured databases and streams are the collections (views included) the
 * credentials are authorized to read. Fields are discovered by sampling documents, the same way the
 * legacy `source-mongodb-v2` connector did.
 */
class MongoDbSourceMetadataQuerier(
    val configuration: MongoDbSourceConfiguration,
    val client: MongoClient,
    /**
     * When true, [fields] returns an empty list without sampling. CHECK only calls [fields] to
     * probe that a stream is queryable; the legacy connector never sampled documents during
     * `check`, and sampling up to `discover_sample_size` documents there would be slow.
     */
    private val skipFieldDiscovery: Boolean = false,
) : MetadataQuerier {

    /** Collections are sampled concurrently, like the legacy connector's `parallelStream()`. */
    private val executorDelegate: Lazy<ExecutorService> = lazy {
        Executors.newFixedThreadPool(DISCOVER_PARALLELISM)
    }
    private val executor: ExecutorService by executorDelegate
    private val fieldsByStream = ConcurrentHashMap<StreamIdentifier, Future<List<EmittedField>>>()
    private val prefetchedNamespaces: MutableSet<String> = ConcurrentHashMap.newKeySet()

    override fun streamNamespaces(): List<String> = configuration.databases

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        if (streamNamespace == null) {
            return emptyList()
        }
        return authorizedCollections(streamNamespace).sorted().map { collectionName: String ->
            StreamIdentifier.from(
                StreamDescriptor().withName(collectionName).withNamespace(streamNamespace),
            )
        }
    }

    /**
     * Names of the collections in [databaseName] which the current credentials may read. Same
     * `listCollections` invocation as the legacy connector (the legacy connector never applied its
     * `type: collection` filter, so views are included here too).
     */
    fun authorizedCollections(databaseName: String): Set<String> {
        val command =
            Document("listCollections", 1)
                .append("authorizedCollections", true)
                .append("nameOnly", true)
        val result: BsonDocument =
            client.getDatabase(databaseName).runCommand(command).toBsonDocument()
        return result
            .getDocument("cursor")
            .getArray("firstBatch")
            .map { it.asDocument().getString("name").value }
            .filter(::isSupportedCollection)
            .toSet()
    }

    /**
     * Fields of the collection, discovered by sampling its documents; empty for an empty
     * collection, which DISCOVER then omits from the catalog (as the legacy connector did).
     *
     * The first call for a namespace schedules the sampling of all its collections so that
     * DISCOVER, which calls this method once per stream, runs them concurrently.
     */
    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        if (skipFieldDiscovery) {
            return emptyList()
        }
        val namespace: String = streamID.namespace ?: return emptyList()
        if (prefetchedNamespaces.add(namespace)) {
            for (otherStreamID in streamNames(namespace)) {
                scheduleFieldDiscovery(otherStreamID)
            }
        }
        return try {
            scheduleFieldDiscovery(streamID).get()
        } catch (e: ExecutionException) {
            throw e.cause ?: e
        }
    }

    private fun scheduleFieldDiscovery(streamID: StreamIdentifier): Future<List<EmittedField>> =
        fieldsByStream.computeIfAbsent(streamID) {
            executor.submit(Callable { discoverFields(it) })
        }

    /** Samples the collection and maps its fields to [MongoDbFieldType]s, sorted by name. */
    internal fun discoverFields(streamID: StreamIdentifier): List<EmittedField> {
        val collection: MongoCollection<Document> =
            client.getDatabase(streamID.namespace!!).getCollection(streamID.name)
        val fieldTypes: Map<String, MongoDbFieldType> =
            if (configuration.schemaEnforced) {
                sampleFieldTypes(collection)
            } else {
                sampleIdFieldType(collection)
            }
        if (fieldTypes.isEmpty()) {
            return emptyList()
        }
        val fields: List<EmittedField> =
            fieldTypes.entries.sortedBy { it.key }.map { (name, type) -> EmittedField(name, type) }
        if (configuration.schemaEnforced) {
            return fields
        }
        // Schemaless mode: the whole document is emitted in a single `data` object field.
        return fields + EmittedField(DATA_FIELD, MongoDbFieldType.OBJECT)
    }

    /**
     * Discovers the top-level field names and BSON types present in a random sample of
     * `discover_sample_size` documents, with the legacy aggregation:
     * ```
     * [ {$sample: {size: N}},
     *   {$project: {fields: {$arrayToObject: {$map: {input: {$objectToArray: "$$ROOT"}, as: "each",
     *                                                 in: {k: "$$each.k", v: {$type: "$$each.v"}}}}}}},
     *   {$unwind: "$fields"},
     *   {$group: {_id: "$fields"}} ]
     * ```
     * Each result is one distinct document shape (field name -> BSON type name). When a field
     * appears with several types, the first shape returned by the server wins, as in the legacy
     * connector (which collected `MongoField`s, equal by name only, in a `HashSet`).
     */
    private fun sampleFieldTypes(
        collection: MongoCollection<Document>
    ): Map<String, MongoDbFieldType> {
        val typeOfEachField =
            Document(
                "\$map",
                Document("input", Document("\$objectToArray", "\$\$ROOT"))
                    .append("as", "each")
                    .append(
                        "in",
                        Document("k", "\$\$each.k").append("v", Document("\$type", "\$\$each.v"))
                    )
            )
        val pipeline: List<Bson> =
            listOf(
                Aggregates.sample(configuration.discoverSampleSize),
                Aggregates.project(
                    Document("fields", Document("\$arrayToObject", typeOfEachField))
                ),
                Aggregates.unwind("\$fields"),
                Document("\$group", Document("_id", "\$fields")),
            )
        val fieldTypes = LinkedHashMap<String, MongoDbFieldType>()
        sample(collection, pipeline) { shape: Document ->
            val bsonTypeByField: Document = shape.get("_id", Document::class.java)
            for ((fieldName: String, bsonTypeName: Any?) in bsonTypeByField) {
                fieldTypes.putIfAbsent(
                    fieldName,
                    MongoDbFieldType.fromBsonTypeName(bsonTypeName.toString())
                )
            }
        }
        return fieldTypes
    }

    /** Schemaless mode only needs the type of `_id`, which every document has: sample one. */
    private fun sampleIdFieldType(
        collection: MongoCollection<Document>
    ): Map<String, MongoDbFieldType> {
        val pipeline: List<Bson> =
            listOf(
                Aggregates.sample(1),
                Aggregates.project(
                    Projections.fields(
                        Projections.excludeId(),
                        Projections.computed(ID_TYPE_FIELD, Document("\$type", "\$$ID_FIELD")),
                    ),
                ),
            )
        val fieldTypes = LinkedHashMap<String, MongoDbFieldType>()
        sample(collection, pipeline) { document: Document ->
            fieldTypes[ID_FIELD] =
                MongoDbFieldType.fromBsonTypeName(document.getString(ID_TYPE_FIELD))
        }
        return fieldTypes
    }

    /**
     * Runs [pipeline] with the configured `discover_timeout_seconds` budget. Like the legacy
     * connector, errors (timeouts included) are logged and whatever was collected is kept.
     */
    private fun sample(
        collection: MongoCollection<Document>,
        pipeline: List<Bson>,
        consumer: (Document) -> Unit
    ) {
        try {
            collection
                .aggregate(pipeline)
                .allowDiskUse(true)
                .maxTime(configuration.discoverTimeout.toSeconds(), TimeUnit.SECONDS)
                .cursor()
                .use { cursor ->
                    while (cursor.hasNext()) {
                        consumer(cursor.next())
                    }
                }
        } catch (e: Exception) {
            log.warn(e) {
                "Running discovery for document: ${collection.namespace.fullName}. Error processing cursor: ${e.message}"
            }
        }
    }

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> =
        listOf(listOf(ID_FIELD))

    override fun extraChecks() {
        val clusterType: ClusterType = client.clusterDescription.type
        if (clusterType != ClusterType.REPLICA_SET) {
            log.error {
                "Target MongoDB instance is not a replica set cluster (type=$clusterType)."
            }
            throw ConfigErrorException("Target MongoDB instance is not a replica set cluster.")
        }
    }

    override fun close() {
        if (executorDelegate.isInitialized()) {
            executor.shutdownNow()
        }
        client.close()
    }

    /** MongoDB implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory
    @Inject
    constructor(
        @Value("\${${Operation.PROPERTY}:discover}") private val operation: String = "discover",
    ) : MetadataQuerier.Factory<MongoDbSourceConfiguration> {
        /**
         * The [MongoDbSourceConfiguration] is deliberately not injected in order to support tests.
         */
        override fun session(config: MongoDbSourceConfiguration): MetadataQuerier =
            MongoDbSourceMetadataQuerier(
                config,
                MongoDbClientFactory.create(config),
                skipFieldDiscovery = operation == CHECK_OPERATION,
            )
    }

    companion object {
        const val ID_FIELD = "_id"
        /** Name of the field holding the whole document in schemaless mode. */
        const val DATA_FIELD = "data"
        private const val ID_TYPE_FIELD = "_idType"
        private const val CHECK_OPERATION = "check"

        /** Collection name prefixes which are never exposed as streams. */
        val IGNORED_COLLECTION_PREFIXES: Set<String> = setOf("system.", "replset.", "oplog.")

        val DISCOVER_PARALLELISM: Int = Runtime.getRuntime().availableProcessors().coerceAtLeast(1)

        fun isSupportedCollection(collectionName: String): Boolean =
            IGNORED_COLLECTION_PREFIXES.none { collectionName.startsWith(it) }
    }
}
