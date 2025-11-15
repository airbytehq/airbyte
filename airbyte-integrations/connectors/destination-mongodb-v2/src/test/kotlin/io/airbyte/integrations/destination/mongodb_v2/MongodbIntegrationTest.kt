/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mongodb_v2.client.MongodbAirbyteClient
import io.airbyte.integrations.destination.mongodb_v2.spec.MongodbConfiguration
import io.airbyte.integrations.destination.mongodb_v2.write.MongodbInsertBuffer
import java.math.BigInteger
import java.time.OffsetDateTime
import kotlinx.coroutines.runBlocking
import org.bson.Document
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*
import org.testcontainers.containers.MongoDBContainer
import org.testcontainers.utility.DockerImageName

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MongodbIntegrationTest {

    private lateinit var mongoContainer: MongoDBContainer
    private lateinit var mongoClient: MongoClient
    private lateinit var airbyteClient: MongodbAirbyteClient
    private lateinit var config: MongodbConfiguration

    @BeforeAll
    fun startContainer() {
        mongoContainer = MongoDBContainer(DockerImageName.parse("mongo:7.0"))
        mongoContainer.start()

        val connectionString = mongoContainer.replicaSetUrl
        config =
            MongodbConfiguration(
                connectionString = connectionString,
                database = "test_database",
                batchSize = 100
            )

        mongoClient = MongoClients.create(connectionString)
        airbyteClient = MongodbAirbyteClient(mongoClient, config)
    }

    @AfterAll
    fun stopContainer() {
        mongoClient.close()
        mongoContainer.stop()
    }

    @BeforeEach
    fun cleanup() {
        // Drop database before each test for clean slate
        mongoClient.getDatabase(config.database).drop()
    }

    @Test
    fun `test create and drop collection`() = runBlocking {
        val tableName = TableName("test_namespace", "test_collection")

        // Create collection
        val stream = createTestStream("test_stream", Append)
        airbyteClient.createTable(stream, tableName, ColumnNameMapping(emptyMap()), replace = false)

        // Verify collection exists
        assertTrue(airbyteClient.tableExists(tableName))

        // Drop collection
        airbyteClient.dropTable(tableName)

        // Verify collection is gone
        assertFalse(airbyteClient.tableExists(tableName))
    }

    @Test
    fun `test insert and count documents`() = runBlocking {
        val tableName = TableName("test_namespace", "test_collection")
        val stream = createTestStream("test_stream", Append)

        // Create collection
        airbyteClient.createTable(stream, tableName, ColumnNameMapping(emptyMap()), replace = false)

        // Insert documents using InsertBuffer
        val buffer = MongodbInsertBuffer(tableName, mongoClient, config)

        repeat(10) { i -> buffer.accumulate(createTestRecord(i)) }

        buffer.flush()

        // Verify count
        val count = airbyteClient.countTable(tableName)
        assertEquals(10L, count)
    }

    @Test
    fun `test append mode - multiple inserts accumulate`() = runBlocking {
        val tableName = TableName("test_namespace", "append_test")
        val stream = createTestStream("append_stream", Append)

        airbyteClient.createTable(stream, tableName, ColumnNameMapping(emptyMap()), replace = false)

        val buffer = MongodbInsertBuffer(tableName, mongoClient, config)

        // First batch
        repeat(5) { i -> buffer.accumulate(createTestRecord(i)) }
        buffer.flush()

        assertEquals(5L, airbyteClient.countTable(tableName))

        // Second batch
        repeat(5) { i -> buffer.accumulate(createTestRecord(i + 5)) }
        buffer.flush()

        // Should have 10 total records
        assertEquals(10L, airbyteClient.countTable(tableName))
    }

    @Test
    fun `test dedupe mode with primary key`() = runBlocking {
        val sourceTableName = TableName("test_namespace", "dedupe_source")
        val targetTableName = TableName("test_namespace", "dedupe_target")

        val stream =
            createTestStream(
                name = "dedupe_stream",
                importType =
                    Dedupe(primaryKey = listOf(listOf("id")), cursor = listOf("updated_at"))
            )

        val columnMapping =
            ColumnNameMapping(mapOf("id" to "id", "name" to "name", "updated_at" to "updated_at"))

        // Create both collections
        airbyteClient.createTable(stream, sourceTableName, columnMapping, replace = false)
        airbyteClient.createTable(stream, targetTableName, columnMapping, replace = false)

        // Insert duplicate records into source with different timestamps
        val sourceCollection =
            mongoClient.getDatabase(config.database).getCollection(sourceTableName.name)

        sourceCollection.insertMany(
            listOf(
                Document(
                    mapOf(
                        "id" to 1,
                        "name" to "First version",
                        "updated_at" to "2024-01-01T00:00:00Z",
                        Meta.COLUMN_NAME_AB_RAW_ID to "raw_1",
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT to "2024-01-01T00:00:00Z",
                        Meta.COLUMN_NAME_AB_META to Document(),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to 1
                    )
                ),
                Document(
                    mapOf(
                        "id" to 1,
                        "name" to "Second version",
                        "updated_at" to "2024-01-02T00:00:00Z",
                        Meta.COLUMN_NAME_AB_RAW_ID to "raw_2",
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT to "2024-01-02T00:00:00Z",
                        Meta.COLUMN_NAME_AB_META to Document(),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to 1
                    )
                ),
                Document(
                    mapOf(
                        "id" to 2,
                        "name" to "Different record",
                        "updated_at" to "2024-01-01T00:00:00Z",
                        Meta.COLUMN_NAME_AB_RAW_ID to "raw_3",
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT to "2024-01-01T00:00:00Z",
                        Meta.COLUMN_NAME_AB_META to Document(),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to 1
                    )
                )
            )
        )

        // Verify source has 3 documents
        assertEquals(3L, airbyteClient.countTable(sourceTableName))

        // Perform upsert (deduplication)
        airbyteClient.upsertTable(stream, columnMapping, sourceTableName, targetTableName)

        // Verify target has only 2 unique records (deduplicated by PK)
        val targetCollection =
            mongoClient.getDatabase(config.database).getCollection(targetTableName.name)
        val targetCount = targetCollection.countDocuments()
        assertEquals(2L, targetCount)

        // Verify the latest version (by cursor) was kept for id=1
        val record = targetCollection.find(Document("id", 1)).first()
        assertEquals("Second version", record?.getString("name"))
    }

    @Test
    fun `test overwrite mode using rename`() = runBlocking {
        val sourceTableName = TableName("test_namespace", "overwrite_source")
        val targetTableName = TableName("test_namespace", "overwrite_target")

        val stream = createTestStream("overwrite_stream", Append)

        // Create target with some data
        airbyteClient.createTable(
            stream,
            targetTableName,
            ColumnNameMapping(emptyMap()),
            replace = false
        )
        val targetBuffer = MongodbInsertBuffer(targetTableName, mongoClient, config)
        repeat(5) { i -> targetBuffer.accumulate(createTestRecord(i)) }
        targetBuffer.flush()

        assertEquals(5L, airbyteClient.countTable(targetTableName))

        // Create source with different data
        airbyteClient.createTable(
            stream,
            sourceTableName,
            ColumnNameMapping(emptyMap()),
            replace = false
        )
        val sourceBuffer = MongodbInsertBuffer(sourceTableName, mongoClient, config)
        repeat(3) { i -> sourceBuffer.accumulate(createTestRecord(i + 100)) }
        sourceBuffer.flush()

        assertEquals(3L, airbyteClient.countTable(sourceTableName))

        // Overwrite target with source
        airbyteClient.overwriteTable(sourceTableName, targetTableName)

        // Target should now have source's data
        assertEquals(3L, airbyteClient.countTable(targetTableName))

        // Source should be gone (renamed to target)
        assertFalse(airbyteClient.tableExists(sourceTableName))
    }

    @Test
    fun `test indexes created for dedupe mode`() = runBlocking {
        val tableName = TableName("test_namespace", "index_test")
        val stream =
            createTestStream(
                name = "index_stream",
                importType =
                    Dedupe(
                        primaryKey = listOf(listOf("user_id"), listOf("event_id")),
                        cursor = listOf("timestamp")
                    )
            )

        val columnMapping =
            ColumnNameMapping(
                mapOf("user_id" to "user_id", "event_id" to "event_id", "timestamp" to "timestamp")
            )

        airbyteClient.createTable(stream, tableName, columnMapping, replace = false)

        // Verify indexes were created
        val collection = mongoClient.getDatabase(config.database).getCollection(tableName.name)
        val indexes = collection.listIndexes().into(mutableListOf())

        // Should have at least 2 indexes: _id (default) and our compound index
        assertTrue(indexes.size >= 2, "Expected at least 2 indexes, found ${indexes.size}")
    }

    // Helper functions

    private fun createTestStream(
        name: String,
        importType: io.airbyte.cdk.load.command.ImportType
    ): DestinationStream {
        return DestinationStream(
            unmappedNamespace = "test_namespace",
            unmappedName = name,
            importType = importType,
            schema = ObjectTypeWithEmptySchema,
            generationId = 1L,
            minimumGenerationId = 0L,
            syncId = 1L,
            namespaceMapper = NamespaceMapper()
        )
    }

    private fun createTestRecord(id: Int): LinkedHashMap<String, AirbyteValue> {
        return linkedMapOf(
            "id" to IntegerValue(BigInteger.valueOf(id.toLong())),
            "name" to StringValue("Record $id"),
            "value" to NumberValue(java.math.BigDecimal(id * 10)),
            Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw_$id"),
            Meta.COLUMN_NAME_AB_EXTRACTED_AT to TimestampWithTimezoneValue(OffsetDateTime.now()),
            Meta.COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
            Meta.COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1L)
        )
    }
}
