/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import com.mongodb.client.model.ChangeStreamPreAndPostImagesOptions
import com.mongodb.client.model.CreateCollectionOptions
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.FullDocumentBeforeChange
import com.mongodb.client.model.changestream.OperationType
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.integrations.source.mongodb.MongoDbReadTestSupport
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.bson.BsonDocument
import org.bson.Document
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.MongoDBContainer

/** What the pipeline lets cross the network, seen on a change stream opened as the connector's. */
class MongoDbChangeStreamPipelineTest {

    @Test
    fun testPreImagesTravelOnlyWithDeletesAndWithUpdatesOfDocumentsAlreadyGone() {
        MongoClients.create(replicaSet.connectionString).use { client ->
            val db = client.getDatabase(TEST_DB)
            db.getCollection(PEOPLE).drop()
            db.createCollection(
                PEOPLE,
                CreateCollectionOptions()
                    .changeStreamPreAndPostImagesOptions(ChangeStreamPreAndPostImagesOptions(true)),
            )
            val people: MongoCollection<Document> = db.getCollection(PEOPLE)
            val other: MongoCollection<Document> = db.getCollection(OTHER)
            val stream: ChangeStreamIterable<Document> =
                db.watch(
                        MongoDbChangeStreamPipeline.build(
                            listOf(streamId(TEST_DB, PEOPLE)),
                            preImages = true,
                        ),
                    )
                    .fullDocument(FullDocument.UPDATE_LOOKUP)
                    .fullDocumentBeforeChange(FullDocumentBeforeChange.WHEN_AVAILABLE)
                    .batchSize(Int.MAX_VALUE)
            val start: BsonDocument =
                stream.cursor().use {
                    it.tryNext()
                    checkNotNull(it.resumeToken)
                }

            people.insertOne(Document("_id", 1).append("name", "alice"))
            people.updateOne(Filters.eq("_id", 1), Updates.set("name", "alicia"))
            other.insertOne(Document("_id", 1).append("name", "unwatched"))
            people.insertOne(Document("_id", 2).append("name", "bob"))
            // Looked up only once the stream is read below, when the document is already gone.
            people.updateOne(Filters.eq("_id", 2), Updates.set("name", "robert"))
            people.deleteOne(Filters.eq("_id", 2))
            other.drop()

            val events: List<ChangeStreamDocument<Document>> =
                stream.resumeAfter(start).cursor().use { cursor ->
                    generateSequence { cursor.tryNext() }.toList()
                }
            Assertions.assertEquals(
                listOf(
                    OperationType.INSERT,
                    OperationType.UPDATE,
                    OperationType.INSERT,
                    OperationType.UPDATE,
                    OperationType.DELETE,
                ),
                events.map { it.operationType },
                "only the watched collection's data changes: $events",
            )
            Assertions.assertNull(events[0].fullDocumentBeforeChange)
            // An ordinary update is emitted from its post-image: the pre-image is dropped.
            Assertions.assertEquals("alicia", events[1].fullDocument?.getString("name"))
            Assertions.assertNull(events[1].fullDocumentBeforeChange)
            // The lookup found nothing: the pre-image is what the record is built from.
            Assertions.assertNull(events[3].fullDocument)
            Assertions.assertEquals("bob", events[3].fullDocumentBeforeChange?.getString("name"))
            Assertions.assertEquals("robert", events[4].fullDocumentBeforeChange?.getString("name"))
        }
    }

    private fun streamId(database: String, collection: String): StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName(collection).withNamespace(database))

    companion object {
        const val TEST_DB = "pipeline_db"
        const val PEOPLE = "people"
        const val OTHER = "other"

        lateinit var replicaSet: MongoDBContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            replicaSet = MongoDbReadTestSupport.replicaSet().also { it.start() }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            replicaSet.stop()
        }
    }
}
