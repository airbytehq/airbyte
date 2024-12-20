/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.alibaba.dcm.DnsCacheManipulator
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.mongodb.client.MongoClient
import com.mongodb.client.MongoClients
import com.mongodb.client.MongoCollection
import com.mongodb.client.MongoDatabase
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.cdk.discover.TestMetaFieldDecorator
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.testcontainers.TestContainerFactory
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.debezium.connector.mongodb.MongoDbConnector
import io.debezium.connector.mongodb.ResumeTokens
import io.debezium.connector.mysql.MySqlConnector
import io.debezium.connector.postgresql.PostgresConnector
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.debezium.testing.testcontainers.MongoDbReplicaSet
import java.sql.Connection
import java.sql.Statement
import java.time.Duration
import java.time.Instant
import java.util.regex.Pattern
import kotlin.random.Random
import kotlin.random.nextInt
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.apache.kafka.connect.source.SourceRecord
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.conversions.Bson
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.postgresql.replication.LogSequenceNumber
import org.testcontainers.containers.MySQLContainer
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName

/**
 * This test class verifies that the [CdcPartitionReader] is able to correctly start and stop the
 * Debezium Engine. As there is no useful way to mock the Debezium Engine, the test is actually an
 * integration test and this class is subclassed for multiple Debezium implementations which connect
 * to a corresponding testcontainer data source.
 */
sealed class CdcPartitionReaderTest<T : Comparable<T>, C : AutoCloseable>(
    namespace: String?,
    val heartbeat: Duration = Duration.ofMillis(100),
    val timeout: Duration = Duration.ofSeconds(10),
) : CdcPartitionReaderDebeziumOperations<T> {

    val stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("tbl").withNamespace(namespace)),
            schema = setOf(Field("v", IntFieldType), TestMetaFieldDecorator.GlobalCursor),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = TestMetaFieldDecorator.GlobalCursor,
        )

    val global: Global
        get() = Global(listOf(stream))

    abstract fun createContainer(): C
    abstract fun C.createStream()
    abstract fun C.insert12345()
    abstract fun C.update135()
    abstract fun C.delete24()

    abstract fun C.currentPosition(): T
    abstract fun C.syntheticInput(): DebeziumInput
    abstract fun C.debeziumProperties(): Map<String, String>

    @Test
    /**
     * The [integrationTest] method sets up (and tears down) a testcontainer for the data source
     * using [createContainer] and provisions it using [createStream], [insert12345], [update135]
     * and [delete24].
     *
     * While doing so, it creates several [CdcPartitionReader] instances using [currentPosition],
     * [syntheticInput] and [debeziumProperties], and exercises all [PartitionReader] methods.
     */
    fun integrationTest() {
        createContainer().use { container: C ->
            container.createStream()
            val p0: T = container.currentPosition()
            val r0: ReadResult = read(container.syntheticInput(), p0)
            Assertions.assertEquals(emptyList<Record>(), r0.records)
            Assertions.assertNotEquals(
                CdcPartitionReader.CloseReason.RECORD_REACHED_TARGET_POSITION,
                r0.closeReason,
            )

            container.insert12345()
            val insert =
                listOf<Record>(
                    Insert(1, 1),
                    Insert(2, 2),
                    Insert(3, 3),
                    Insert(4, 4),
                    Insert(5, 5),
                )
            container.update135()
            val update =
                listOf<Record>(
                    Update(1, 6),
                    Update(3, 7),
                    Update(5, 8),
                )
            val p1: T = container.currentPosition()
            container.delete24()
            val delete =
                listOf<Record>(
                    Delete(2),
                    Delete(4),
                )
            val p2: T = container.currentPosition()

            val input = DebeziumInput(container.debeziumProperties(), r0.state, isSynthetic = false)
            val r1: ReadResult = read(input, p1)
            Assertions.assertEquals(insert + update, r1.records.take(insert.size + update.size))
            Assertions.assertNotNull(r1.closeReason)

            val r2: ReadResult = read(input, p2)
            Assertions.assertEquals(
                insert + update + delete,
                r2.records.take(insert.size + update.size + delete.size),
            )
            Assertions.assertNotNull(r2.closeReason)
            Assertions.assertNotEquals(
                CdcPartitionReader.CloseReason.RECORD_REACHED_TARGET_POSITION,
                r2.closeReason
            )
        }
    }

    private fun read(
        input: DebeziumInput,
        upperBound: T,
    ): ReadResult {
        val outputConsumer = BufferingOutputConsumer(ClockFactory().fixed())
        val streamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer> =
            mapOf(
                stream.id to
                    object : StreamRecordConsumer {
                        override val stream: Stream = this@CdcPartitionReaderTest.stream

                        override fun accept(
                            recordData: ObjectNode,
                            changes: Map<Field, FieldValueChange>?
                        ) {
                            outputConsumer.accept(
                                AirbyteRecordMessage()
                                    .withStream(stream.name)
                                    .withNamespace(stream.namespace)
                                    .withData(recordData)
                            )
                        }
                    }
            )
        val reader =
            CdcPartitionReader(
                ConcurrencyResource(1),
                streamRecordConsumers,
                this,
                upperBound,
                input,
            )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources(),
        )
        val checkpoint: PartitionReadCheckpoint
        try {
            runBlocking {
                try {
                    withTimeout(timeout.toMillis()) { reader.run() }
                } catch (_: TimeoutCancellationException) {}
            }
            checkpoint = reader.checkpoint()
        } finally {
            reader.releaseResources()
        }
        // Sanity checks. If any of these fail, particularly after a debezium version change,
        // it's important to understand why.
        Assertions.assertEquals(checkpoint.numRecords.toInt(), outputConsumer.records().size)
        Assertions.assertEquals(checkpoint.numRecords, reader.numEmittedRecords.get())
        Assertions.assertEquals(
            reader.numEvents.get(),
            reader.numEmittedRecords.get() +
                reader.numDiscardedRecords.get() +
                reader.numHeartbeats.get() +
                reader.numTombstones.get()
        )
        Assertions.assertEquals(0, reader.numDiscardedRecords.get())
        Assertions.assertEquals(0, reader.numEventsWithoutSourceRecord.get())
        Assertions.assertEquals(0, reader.numSourceRecordsWithoutPosition.get())
        Assertions.assertEquals(0, reader.numEventValuesWithoutPosition.get())
        return ReadResult(
            outputConsumer.records().map { Jsons.treeToValue(it.data, Record::class.java) },
            deserialize(checkpoint.opaqueStateValue),
            reader.closeReasonReference.get(),
        )
    }

    data class ReadResult(
        val records: List<Record>,
        val state: DebeziumState,
        val closeReason: CdcPartitionReader.CloseReason?,
    )

    @JsonTypeInfo(use = JsonTypeInfo.Id.MINIMAL_CLASS)
    @JsonSubTypes(
        JsonSubTypes.Type(value = Insert::class),
        JsonSubTypes.Type(value = Update::class),
        JsonSubTypes.Type(value = Delete::class),
    )
    sealed interface Record {
        val id: Int
    }
    data class Insert(override val id: Int, val v: Int) : Record
    data class Update(override val id: Int, val v: Int) : Record
    data class Delete(override val id: Int) : Record

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val id: Int = key.element("id").asInt()
        val after: Int? = value.after["v"]?.asInt()
        val record: Record =
            if (after == null) {
                Delete(id)
            } else if (value.before["v"] == null) {
                Insert(id, after)
            } else {
                Update(id, after)
            }
        return DeserializedRecord(
            data = Jsons.valueToTree(record) as ObjectNode,
            changes = emptyMap(),
        )
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        stream.id.namespace

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        stream.id.name

    override fun serialize(debeziumState: DebeziumState): OpaqueStateValue =
        Jsons.valueToTree(
            mapOf(
                "offset" to
                    debeziumState.offset.wrapped
                        .map {
                            Jsons.writeValueAsString(it.key) to Jsons.writeValueAsString(it.value)
                        }
                        .toMap(),
                "schemaHistory" to
                    debeziumState.schemaHistory?.wrapped?.map {
                        DocumentWriter.defaultWriter().write(it.document())
                    },
            ),
        )

    private fun deserialize(opaqueStateValue: OpaqueStateValue): DebeziumState {
        val offsetNode: ObjectNode = opaqueStateValue["offset"] as ObjectNode
        val offset =
            DebeziumOffset(
                offsetNode
                    .fields()
                    .asSequence()
                    .map { Jsons.readTree(it.key) to Jsons.readTree(it.value.asText()) }
                    .toMap(),
            )
        val historyNode: ArrayNode =
            opaqueStateValue["schemaHistory"] as? ArrayNode
                ?: return DebeziumState(offset, schemaHistory = null)
        val schemaHistory =
            DebeziumSchemaHistory(
                historyNode.elements().asSequence().toList().map {
                    HistoryRecord(DocumentReader.defaultReader().read(it.asText()))
                },
            )
        return DebeziumState(offset, schemaHistory)
    }
}

class CdcPartitionReaderMySQLTest :
    CdcPartitionReaderTest<CdcPartitionReaderMySQLTest.Position, MySQLContainer<*>>(
        namespace = "test",
    ) {

    data class Position(val file: String, val pos: Long) : Comparable<Position> {
        override fun compareTo(other: Position): Int =
            file.compareTo(other.file).takeUnless { it == 0 } ?: pos.compareTo(other.pos)
    }

    override fun createContainer(): MySQLContainer<*> {
        val dockerImageName: DockerImageName =
            DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(DOCKER_IMAGE_NAME)
        val modifier: TestContainerFactory.ContainerModifier<MySQLContainer<*>> =
            TestContainerFactory.newModifier("withRoot") { it.withUsername("root") }
        return TestContainerFactory.exclusive(dockerImageName, modifier)
    }

    companion object {
        const val DOCKER_IMAGE_NAME = "mysql:8.0"
        init {
            TestContainerFactory.register(DOCKER_IMAGE_NAME, ::MySQLContainer)
        }
    }

    override fun MySQLContainer<*>.createStream() {
        withStatement { it.execute("CREATE TABLE tbl (id INT AUTO_INCREMENT PRIMARY KEY, v INT)") }
    }

    override fun MySQLContainer<*>.insert12345() {
        for (i in 1..5) {
            withStatement { it.execute("INSERT INTO tbl (v) VALUES ($i)") }
        }
    }

    override fun MySQLContainer<*>.update135() {
        withStatement { it.execute("UPDATE tbl SET v = 6 WHERE id = 1") }
        withStatement { it.execute("UPDATE tbl SET v = 7 WHERE id = 3") }
        withStatement { it.execute("UPDATE tbl SET v = 8 WHERE id = 5") }
    }

    override fun MySQLContainer<*>.delete24() {
        withStatement { it.execute("DELETE FROM tbl WHERE id = 2") }
        withStatement { it.execute("DELETE FROM tbl WHERE id = 4") }
    }

    private fun <X> MySQLContainer<*>.withStatement(fn: (Statement) -> X): X =
        createConnection("").use { connection: Connection ->
            connection.createStatement().use { fn(it) }
        }

    override fun position(recordValue: DebeziumRecordValue): Position? {
        val file: String =
            recordValue.source["file"]?.takeIf { it.isTextual }?.asText() ?: return null
        val pos: Long =
            recordValue.source["pos"]?.takeIf { it.isIntegralNumber }?.asLong() ?: return null
        return Position(file, pos)
    }

    override fun position(sourceRecord: SourceRecord): Position? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val file: String = offset["file"]?.toString() ?: return null
        val pos: Long = offset["pos"] as? Long ?: return null
        return Position(file, pos)
    }

    override fun MySQLContainer<*>.currentPosition(): Position =
        withStatement { statement: Statement ->
            statement.executeQuery("SHOW MASTER STATUS").use {
                it.next()
                Position(it.getString("File"), it.getLong("Position"))
            }
        }

    override fun MySQLContainer<*>.syntheticInput(): DebeziumInput {
        val position: Position = currentPosition()
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", databaseName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_sec", timestamp.epochSecond)
                put("file", position.file)
                put("pos", position.pos)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        val state = DebeziumState(offset, schemaHistory = null)
        val syntheticProperties: Map<String, String> =
            DebeziumPropertiesBuilder()
                .with(debeziumProperties())
                .with("snapshot.mode", "recovery")
                .withStreams(listOf())
                .buildMap()
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    override fun MySQLContainer<*>.debeziumProperties(): Map<String, String> =
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(MySqlConnector::class.java)
            .withDebeziumName(databaseName)
            .withHeartbeats(heartbeat)
            .with("include.schema.changes", "false")
            .with("connect.keep.alive.interval.ms", "1000")
            .withDatabase("hostname", host)
            .withDatabase("port", firstMappedPort.toString())
            .withDatabase("user", username)
            .withDatabase("password", password)
            .withDatabase("dbname", databaseName)
            .withDatabase("server.id", Random.Default.nextInt(5400..6400).toString())
            .withDatabase("include.list", databaseName)
            .withOffset()
            .withSchemaHistory()
            .with("snapshot.mode", "when_needed")
            .withStreams(listOf(stream))
            .buildMap()
}

class CdcPartitionReaderPostgresTest :
    CdcPartitionReaderTest<LogSequenceNumber, PostgreSQLContainer<*>>(
        namespace = "public",
    ) {

    override fun createContainer(): PostgreSQLContainer<*> {
        val dockerImageName: DockerImageName =
            DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(DOCKER_IMAGE_NAME)
        val modifier: TestContainerFactory.ContainerModifier<PostgreSQLContainer<*>> =
            TestContainerFactory.newModifier("withWalLevelLogical") {
                it.withCommand("postgres -c wal_level=logical")
            }
        return TestContainerFactory.exclusive(dockerImageName, modifier)
    }

    companion object {
        const val DOCKER_IMAGE_NAME = "postgres:13-alpine"
        init {
            TestContainerFactory.register(DOCKER_IMAGE_NAME, ::PostgreSQLContainer)
        }
        const val PUBLICATION_NAME = "test_publication"
        const val SLOT_NAME = "test_slot"
    }

    override fun PostgreSQLContainer<*>.createStream() {
        withStatement { it.execute("CREATE TABLE tbl (id SERIAL PRIMARY KEY, v INT)") }
        withStatement { it.execute("ALTER TABLE tbl REPLICA IDENTITY FULL") }
        withStatement {
            it.execute("SELECT pg_create_logical_replication_slot('$SLOT_NAME', 'pgoutput')")
        }
        withStatement { it.execute("CREATE PUBLICATION $PUBLICATION_NAME FOR TABLE tbl") }
    }

    override fun PostgreSQLContainer<*>.insert12345() {
        for (i in 1..5) {
            withStatement { it.execute("INSERT INTO tbl (v) VALUES ($i)") }
        }
    }

    override fun PostgreSQLContainer<*>.update135() {
        withStatement { it.execute("UPDATE tbl SET v = 6 WHERE id = 1") }
        withStatement { it.execute("UPDATE tbl SET v = 7 WHERE id = 3") }
        withStatement { it.execute("UPDATE tbl SET v = 8 WHERE id = 5") }
    }

    override fun PostgreSQLContainer<*>.delete24() {
        withStatement { it.execute("DELETE FROM tbl WHERE id = 2") }
        withStatement { it.execute("DELETE FROM tbl WHERE id = 4") }
    }

    private fun <X> PostgreSQLContainer<*>.withStatement(fn: (Statement) -> X): X =
        createConnection("").use { connection: Connection ->
            connection.createStatement().use { fn(it) }
        }

    override fun position(recordValue: DebeziumRecordValue): LogSequenceNumber? {
        val lsn: Long =
            recordValue.source["lsn"]?.takeIf { it.isIntegralNumber }?.asLong() ?: return null
        return LogSequenceNumber.valueOf(lsn)
    }

    override fun position(sourceRecord: SourceRecord): LogSequenceNumber? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val lsn: Long = offset["lsn"] as? Long ?: return null
        return LogSequenceNumber.valueOf(lsn)
    }

    override fun PostgreSQLContainer<*>.currentPosition(): LogSequenceNumber =
        withStatement { statement: Statement ->
            statement.executeQuery("SELECT pg_current_wal_lsn()").use {
                it.next()
                LogSequenceNumber.valueOf(it.getString(1))
            }
        }

    override fun PostgreSQLContainer<*>.syntheticInput(): DebeziumInput {
        val (position: LogSequenceNumber, txID: Long) =
            withStatement { statement: Statement ->
                statement.executeQuery("SELECT pg_current_wal_lsn(), txid_current()").use {
                    it.next()
                    LogSequenceNumber.valueOf(it.getString(1)) to it.getLong(2)
                }
            }
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", databaseName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_usec", timestamp.toEpochMilli() * 1000L)
                put("lsn", position.asLong())
                put("txId", txID)
            }
        val offset = DebeziumOffset(mapOf(key to value))
        val state = DebeziumState(offset, schemaHistory = null)
        val syntheticProperties: Map<String, String> = debeziumProperties()
        return DebeziumInput(syntheticProperties, state, isSynthetic = true)
    }

    override fun PostgreSQLContainer<*>.debeziumProperties(): Map<String, String> =
        DebeziumPropertiesBuilder()
            .withDefault()
            .withConnector(PostgresConnector::class.java)
            .withDebeziumName(databaseName)
            .withHeartbeats(heartbeat)
            .with("plugin.name", "pgoutput")
            .with("slot.name", SLOT_NAME)
            .with("publication.name", PUBLICATION_NAME)
            .with("publication.autocreate.mode", "disabled")
            .with("flush.lsn.source", "false")
            .withDatabase("hostname", host)
            .withDatabase("port", firstMappedPort.toString())
            .withDatabase("user", username)
            .withDatabase("password", password)
            .withDatabase("dbname", databaseName)
            .withOffset()
            .withStreams(listOf(stream))
            .buildMap()
}

class CdcPartitionReaderMongoTest :
    CdcPartitionReaderTest<BsonTimestamp, MongoDbReplicaSet>(
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
