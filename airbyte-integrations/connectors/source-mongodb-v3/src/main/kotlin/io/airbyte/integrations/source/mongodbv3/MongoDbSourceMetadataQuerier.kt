/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoClient
import com.mongodb.connection.ClusterType
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import org.bson.BsonDocument
import org.bson.Document

private val log = KotlinLogging.logger {}

/**
 * MongoDB implementation of [MetadataQuerier].
 *
 * Namespaces are the configured databases and streams are the collections the credentials are
 * authorized to read. Field discovery (document sampling) is not implemented yet.
 */
class MongoDbSourceMetadataQuerier(
    val configuration: MongoDbSourceConfiguration,
    val client: MongoClient,
) : MetadataQuerier {

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
     * `listCollections` invocation as the legacy connector (the legacy connector never applied
     * its `type: collection` filter, so views are included here too).
     */
    fun authorizedCollections(databaseName: String): Set<String> {
        val command =
            Document("listCollections", 1)
                .append("authorizedCollections", true)
                .append("nameOnly", true)
        val result: BsonDocument = client.getDatabase(databaseName).runCommand(command).toBsonDocument()
        return result
            .getDocument("cursor")
            .getArray("firstBatch")
            .map { it.asDocument().getString("name").value }
            .filter(::isSupportedCollection)
            .toSet()
    }

    override fun fields(streamID: StreamIdentifier): List<EmittedField> {
        // TODO(stage 2): sample documents to infer the schema.
        return emptyList()
    }

    override fun primaryKey(streamID: StreamIdentifier): List<List<String>> = listOf(listOf(ID_FIELD))

    override fun extraChecks() {
        val clusterType: ClusterType = client.clusterDescription.type
        if (clusterType != ClusterType.REPLICA_SET) {
            log.error { "Target MongoDB instance is not a replica set cluster (type=$clusterType)." }
            throw ConfigErrorException("Target MongoDB instance is not a replica set cluster.")
        }
    }

    override fun close() {
        client.close()
    }

    /** MongoDB implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory : MetadataQuerier.Factory<MongoDbSourceConfiguration> {
        /** The [MongoDbSourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: MongoDbSourceConfiguration): MetadataQuerier =
            MongoDbSourceMetadataQuerier(config, MongoDbClientFactory.create(config))
    }

    companion object {
        const val ID_FIELD = "_id"

        /** Collection name prefixes which are never exposed as streams. */
        val IGNORED_COLLECTION_PREFIXES: Set<String> = setOf("system.", "replset.", "oplog.")

        fun isSupportedCollection(collectionName: String): Boolean =
            IGNORED_COLLECTION_PREFIXES.none { collectionName.startsWith(it) }
    }
}
