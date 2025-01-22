/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.alibaba.dcm.DnsCacheManipulator
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoDatabase
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mongodb.MongoDbConnector
import io.debezium.connector.mongodb.ResumeTokens
import io.debezium.testing.testcontainers.MongoDbReplicaSet
import java.util.regex.Pattern
import org.apache.kafka.connect.source.SourceRecord
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.conversions.Bson

class CdcPartitionReaderMongoTest :
    AbstractCdcPartitionReaderTest<BsonTimestamp, MongoDbReplicaSet>(
        namespace = "test",
    ) {

    override fun createContainer(): MongoDbReplicaSet {
        return MongoDbReplicaSet.replicaSet().memberCount(1).build().also {
            for (hostName in it.hostNames) {
                DnsCacheManipulator.setDnsCache(hostName, "127.0.0.1")
            }
            it.start()
        }
    }

    override fun MongoDbReplicaSet.createStream() {
        withMongoCollection { it.insertOne(Document("_id", 0)) }
    }

    override fun MongoDbReplicaSet.insert12345() {
        withMongoCollection {
            for (i in 1..5) {
                it.insertOne(Document("_id", i).append("v", i))
            }
        }
    }

    override fun MongoDbReplicaSet.update135() {
        withMongoCollection {
            it.updateOne(Document("_id", 1), Updates.set("v", 6))
            it.updateOne(Document("_id", 3), Updates.set("v", 7))
            it.updateOne(Document("_id", 5), Updates.set("v", 8))
        }
    }

    override fun MongoDbReplicaSet.delete24() {
        withMongoCollection {
            it.deleteOne(Document("_id", 2))
            it.deleteOne(Document("_id", 4))
        }
    }

    private fun <X> MongoDbReplicaSet.withMongoClient(fn: (MongoClient) -> X): X =
        MongoClients.create(connectionString).use { fn(it) }

    private fun <X> MongoDbReplicaSet.withMongoDatabase(fn: (MongoDatabase) -> X): X =
        withMongoClient {
            fn(it.getDatabase(stream.namespace!!))
        }

    fun <X> MongoDbReplicaSet.withMongoCollection(fn: (MongoCollection<Document>) -> X): X =
        withMongoDatabase {
            fn(it.getCollection(stream.name))
        }

    override fun position(recordValue: DebeziumRecordValue): BsonTimestamp? {
        val resumeToken: String =
            recordValue.source["resume_token"]?.takeIf { it.isTextual }?.asText() ?: return null
        return ResumeTokens.getTimestamp(ResumeTokens.fromData(resumeToken))
    }

    override fun position(sourceRecord: SourceRecord): BsonTimestamp? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val resumeTokenBase64: String = offset["resume_token"] as? String ?: return null
        return ResumeTokens.getTimestamp(ResumeTokens.fromBase64(resumeTokenBase64))
    }

    override fun MongoDbReplicaSet.currentPosition(): BsonTimestamp =
        ResumeTokens.getTimestamp(currentResumeToken())

    override fun MongoDbReplicaSet.syntheticInput(): DebeziumInput {
        val resumeToken: BsonDocument = currentResumeToken()
        val timestamp: BsonTimestamp = ResumeTokens.getTimestamp(resumeToken)
        val resumeTokenString: String = ResumeTokens.getData(resumeToken).asString().value
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(stream.namespace)
                add(Jsons.objectNode().apply { put("server_id", stream.namespace) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ord", timestamp.inc)
                put("sec", timestamp.time)
                put("resume_token", resumeTokenString)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        val state = DebeziumState(offset, schemaHistory = null)
        val syntheticProperties: Map<String, String> = debeziumProperties()
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    private fun MongoDbReplicaSet.currentResumeToken(): BsonDocument =
        withMongoDatabase { mongoDatabase: MongoDatabase ->
            val pipeline = listOf<Bson>(Aggregates.match(Filters.`in`("ns.coll", stream.name)))
            mongoDatabase.watch(pipeline, BsonDocument::class.java).cursor().use {
                it.tryNext()
                it.resumeToken!!
            }
        }

    override fun MongoDbReplicaSet.debeziumProperties(): Map<String, String> =
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(MongoDbConnector::class.java)
            .withDebeziumName(stream.namespace!!)
            .withHeartbeats(heartbeat)
            .with("capture.scope", "database")
            .with("capture.target", stream.namespace!!)
            .with("mongodb.connection.string", connectionString)
            .with("snapshot.mode", "no_data")
            .with(
                "collection.include.list",
                DebeziumPropertiesBuilder.joinIncludeList(
                    listOf(Pattern.quote("${stream.namespace!!}.${stream.name}"))
                )
            )
            .with("database.include.list", stream.namespace!!)
            .withOffset()
            .buildMap()

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val id: Int = key.element("id").asInt()
        val record: Record =
            if (value.operation == "d") {
                Delete(id)
            } else {
                val v: Int? =
                    value.after
                        .takeIf { it.isTextual }
                        ?.asText()
                        ?.let { Jsons.readTree(it)["v"] }
                        ?.asInt()
                if (v == null) {
                    // In case a mongodb document was updated and then deleted, the update change
                    // event will not have any information ({after: null})
                    // We are going to treat it as a Delete.
                    Delete(id)
                } else if (value.operation == "u") {
                    Update(id, v)
                } else {
                    Insert(id, v)
                }
            }
        return DeserializedRecord(
            data = Jsons.valueToTree(record),
            changes = emptyMap(),
        )
    }
}
