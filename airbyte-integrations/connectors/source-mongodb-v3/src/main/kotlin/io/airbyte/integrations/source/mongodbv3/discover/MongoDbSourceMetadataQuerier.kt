/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.discover

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Projections
import com.mongodb.connection.ClusterType
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.integrations.source.mongodbv3.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodbv3.config.MongoDbSourceConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit
import org.bson.BsonDocument
import org.bson.Document
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/**
 * MongoDB implementation of [MetadataQuerier]: namespaces are the configured databases, streams are
 * the collections (views included) the credentials may read, and fields come from sampling
 * documents.
 */
class MongoDbSourceMetadataQuerier(
    val configuration: MongoDbSourceConfiguration,
    val client: MongoClient,
    /**
     * When true, [fields] returns an empty list without sampling: CHECK only calls it to probe that
     * a stream is queryable, and sampling `discover_sample_size` documents there would be slow.
     */
    private val skipFieldDiscovery: Boolean = false,
    /**
     * When set (READ only), [fields] is served from this configured catalog instead of by sampling.
     * Required, not an optimization: at READ start `StateManagerFactory.toStream()` compares the
     * catalog's `json_schema` against [fields] and drops the whole stream on any missing or
     * differently-typed property (aborting the READ, since `global = true`). A fresh random sample
     * can legitimately miss a rare field or re-type a mixed-type one, so only the catalog itself is
     * guaranteed to pass.
     */
    private val readModeCatalog: ConfiguredAirbyteCatalog? = null,
) : MetadataQuerier {

    private val fieldsByStream = ConcurrentHashMap<StreamIdentifier, List<EmittedField>>()
    private val sampledNamespaces: MutableSet<String> = ConcurrentHashMap.newKeySet()

    /** Configured databases in which the credentials can read no collection (see [streamNames]). */
    private val databasesWithoutPermission: MutableList<String> = mutableListOf()

    override fun streamNamespaces(): List<String> = configuration.databases

    /**
     * The collections of [streamNamespace], sorted. During `check`, once the **last** configured
     * database has also turned out empty, this names the unreadable databases instead of letting
     * the CDK report a generic "Discovered zero tables." (`CheckOperation` stops at the first
     * readable stream, so reaching the last database with nothing found means none had any.)
     * `discover` and `read` are unaffected: an empty catalog, and `StreamNotFound` respectively.
     */
    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        if (streamNamespace == null) {
            return emptyList()
        }
        val collections: Set<String> = authorizedCollections(streamNamespace)
        if (collections.isEmpty()) {
            databasesWithoutPermission += streamNamespace
            val allDatabasesEmpty: Boolean =
                skipFieldDiscovery &&
                    streamNamespace == configuration.databases.last() &&
                    databasesWithoutPermission.containsAll(configuration.databases)
            if (allDatabasesEmpty) {
                throw ConfigErrorException(
                    "Target MongoDB databases do not contain any authorized collections. " +
                        "Databases without permissions: ${databasesWithoutPermission.joinToString(", ")}",
                )
            }
        }
        return collections.sorted().map { collectionName: String ->
            StreamIdentifier.from(
                StreamDescriptor().withName(collectionName).withNamespace(streamNamespace),
            )
        }
    }

    /** Names of the collections (views included) in [databaseName] the credentials may read. */
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
     * collection, which DISCOVER then omits. DISCOVER calls this once per stream, so the first call
     * for a namespace samples all of its collections in parallel and caches the results.
     */
    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        if (skipFieldDiscovery) {
            return emptyList()
        }
        readModeCatalog?.let {
            return fieldsFromConfiguredCatalog(streamID, it)
        }
        val namespace: String = streamID.namespace ?: return emptyList()
        if (sampledNamespaces.add(namespace)) {
            streamNames(namespace).parallelStream().forEach {
                fieldsByStream[it] = discoverFields(it)
            }
        }
        return fieldsByStream.computeIfAbsent(streamID, ::discoverFields)
    }

    /**
     * Reconstructs a stream's fields from the configured catalog's JSON schema, dropping the
     * `_ab_*` meta fields (the CDK adds those back). A stream absent from the catalog yields no
     * fields.
     */
    private fun fieldsFromConfiguredCatalog(
        streamID: StreamIdentifier,
        catalog: ConfiguredAirbyteCatalog,
    ): List<EmittedField> {
        val configuredStream =
            catalog.streams.firstOrNull {
                it.stream.name == streamID.name && it.stream.namespace == streamID.namespace
            }
                ?: return emptyList()
        val properties: JsonNode =
            configuredStream.stream.jsonSchema?.get("properties") ?: return emptyList()
        return properties
            .fields()
            .asSequence()
            .filterNot { (name, _) -> name.startsWith(MetaField.META_PREFIX) }
            .map { (name, schema) -> EmittedField(name, MongoDbFieldType.fromJsonSchema(schema)) }
            .toList()
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
     * `discover_sample_size` documents:
     * ```
     * [ {$sample: {size: N}},
     *   {$project: {fields: {$arrayToObject: {$map: {input: {$objectToArray: "$$ROOT"}, as: "each",
     *                                                 in: {k: "$$each.k", v: {$type: "$$each.v"}}}}}}},
     *   {$unwind: "$fields"},
     *   {$group: {_id: "$fields"}} ]
     * ```
     * Each result is one distinct document shape (field name -> BSON type name); when a field
     * appears with several types, the first shape returned by the server wins.
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
     * Runs [pipeline] within the `discover_timeout_seconds` budget; errors (timeouts included) are
     * logged and whatever was collected is kept.
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

    /**
     * Change streams need an oplog: a standalone `mongod` has none, so it can never sync and fails
     * here with a clear message. A sharded cluster reached through `mongos` (`SHARDED`) and a
     * load-balanced deployment (`LOAD_BALANCED`, e.g. Atlas Serverless) do support change streams
     * and pass; any other non-replica-set type is reported but not rejected.
     */
    override fun extraChecks() {
        when (val clusterType: ClusterType = client.clusterDescription.type) {
            ClusterType.REPLICA_SET,
            ClusterType.SHARDED,
            ClusterType.LOAD_BALANCED -> Unit
            ClusterType.STANDALONE ->
                throw ConfigErrorException(
                    "Target MongoDB instance is a standalone server, which has no oplog and does " +
                        "not support change streams. Please connect to a replica set or a sharded " +
                        "cluster.",
                )
            else -> log.warn { "Unexpected MongoDB cluster type $clusterType; proceeding." }
        }
    }

    override fun close() {
        client.close()
    }

    /** MongoDB implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory
    @Inject
    constructor(
        @Value("\${${Operation.PROPERTY}:discover}") private val operation: String = "discover",
        /** Present at READ time; empty for spec/check/discover. */
        private val configuredCatalog: ConfiguredAirbyteCatalog? = null,
    ) : MetadataQuerier.Factory<MongoDbSourceConfiguration> {
        /**
         * The [MongoDbSourceConfiguration] is deliberately not injected in order to support tests.
         */
        override fun session(config: MongoDbSourceConfiguration): MetadataQuerier =
            MongoDbSourceMetadataQuerier(
                config,
                MongoDbClientFactory.create(config),
                skipFieldDiscovery = operation == CHECK_OPERATION,
                readModeCatalog = if (operation == READ_OPERATION) configuredCatalog else null,
            )
    }

    companion object {
        const val ID_FIELD = "_id"
        /** Name of the field holding the whole document in schemaless mode. */
        const val DATA_FIELD = "data"
        private const val ID_TYPE_FIELD = "_idType"
        private const val CHECK_OPERATION = "check"
        private const val READ_OPERATION = "read"

        /** Collection name prefixes which are never exposed as streams. */
        val IGNORED_COLLECTION_PREFIXES: Set<String> = setOf("system.", "replset.", "oplog.")

        fun isSupportedCollection(collectionName: String): Boolean =
            IGNORED_COLLECTION_PREFIXES.none { collectionName.startsWith(it) }
    }
}
