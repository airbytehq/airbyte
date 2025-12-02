/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.ReadPreference
import com.mongodb.client.MongoClients
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.debezium.connector.mongodb.MongoDbConnector
import io.debezium.connector.mongodb.ResumeTokens
import io.debezium.engine.DebeziumEngine
import java.io.IOException
import java.io.ObjectInputStream
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets
import java.nio.file.Files
import java.nio.file.Path
import java.util.Properties
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Consumer
import java.util.stream.Collectors
import kotlin.collections.Map
import kotlin.collections.component1
import kotlin.collections.component2
import kotlinx.cli.ArgParser
import kotlinx.cli.ArgType
import kotlinx.cli.required
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.slf4j.LoggerFactory

class DebeziumMongoDbConnectorTest
internal constructor(
    private val connectionString: String,
    private val databaseName: String,
    private val collectionName: String,
    private val username: String,
    private val password: String
) {

    @Throws(InterruptedException::class, IOException::class)
    fun startTest() {
        val queue: LinkedBlockingQueue<io.debezium.engine.ChangeEvent<String, String>> =
            LinkedBlockingQueue<io.debezium.engine.ChangeEvent<String, String>>(10000)
        val path = path
        LOGGER.info("Using offset storage path '{}'.", path)
        testChangeEventStream()

        // will do an initial sync cause offset is null
        initialSync(queue, path)

        // will do an incremental processing cause after the initialSync run the offset must be
        // updated
        engineWithIncrementalSnapshot(queue, path)
    }

    private fun testChangeEventStream() {
        val mongoClientSettings =
            MongoClientSettings.builder()
                .applyConnectionString(
                    ConnectionString(
                        "mongodb+srv://$username:$password@cluster0.iqgf8.mongodb.net/"
                    )
                )
                .readPreference(ReadPreference.secondaryPreferred())
                .build()
        MongoClients.create(mongoClientSettings).use { client ->
            LOGGER.info("Retrieving change stream...")
            val stream = client.watch(BsonDocument::class.java)
            LOGGER.info("Retrieving cursor...")
            val changeStreamCursor = stream.cursor()

            /*
             * Must call tryNext before attempting to get the resume token from the cursor directly. Otherwise,
             * both will return null!
             */
            val cursorDocument = changeStreamCursor.tryNext()
            if (cursorDocument != null) {
                LOGGER.info("Resume token from cursor document: {}", cursorDocument.resumeToken)
            } else {
                LOGGER.info("Cursor document is null.")
            }
            LOGGER.info("Resume token = {}", changeStreamCursor.resumeToken)
            val timestamp: BsonTimestamp = ResumeTokens.getTimestamp(changeStreamCursor.resumeToken)
            LOGGER.info("sec {}, ord {}", timestamp.time, timestamp.inc)
        }
    }

    @Throws(InterruptedException::class, IOException::class)
    private fun initialSync(
        queue: LinkedBlockingQueue<io.debezium.engine.ChangeEvent<String, String>>,
        path: Path
    ) {
        val executorService = Executors.newSingleThreadExecutor()
        val thrownError = AtomicReference<Throwable?>()
        val engineLatch = CountDownLatch(1)
        val engine: DebeziumEngine<io.debezium.engine.ChangeEvent<String, String>> =
            DebeziumEngine.create<String>(io.debezium.engine.format.Json::class.java)
                .using(
                    getDebeziumProperties(
                        path,
                        listOf("$databaseName\\.$collectionName")
                            .stream()
                            .collect(Collectors.joining(","))
                    )
                )
                .using(io.debezium.engine.spi.OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
                .notifying(
                    Consumer<io.debezium.engine.ChangeEvent<String, String>> {
                        e: io.debezium.engine.ChangeEvent<String, String> ->
                        // debezium outputs a tombstone event that has a value of null. this is an
                        // artifact of how it
                        // interacts with kafka. we want to ignore it.
                        // more on the tombstone:
                        // https://debezium.io/documentation/reference/configuration/event-flattening.html
                        if (e.value() != null) {
                            LOGGER.debug("{}", e)
                            var inserted = false
                            while (!inserted) {
                                inserted = queue.offer(e)
                            }
                        }
                    }
                )
                .using { _: Boolean, message: String?, error: Throwable? ->
                    LOGGER.info("Initial sync Debezium engine shutdown.")
                    if (error != null) {
                        LOGGER.error("error occurred: {}", message, error)
                    }
                    engineLatch.countDown()
                    thrownError.set(error)
                }
                .build()
        executorService.execute(engine)
        Thread.sleep((45 * 1000).toLong())
        engine.close()
        engineLatch.await(5, TimeUnit.MINUTES)
        executorService.shutdown()
        executorService.awaitTermination(5, TimeUnit.MINUTES)
        readOffsetFile(path)
        if (thrownError.get() != null) {
            throw RuntimeException(thrownError.get())
        }
    }

    @Throws(InterruptedException::class, IOException::class)
    private fun engineWithIncrementalSnapshot(
        queue: LinkedBlockingQueue<io.debezium.engine.ChangeEvent<String, String>>,
        path: Path
    ) {
        val executorService2 = Executors.newSingleThreadExecutor()
        val thrownError2 = AtomicReference<Throwable?>()
        val engineLatch2 = CountDownLatch(1)
        val engine2: DebeziumEngine<io.debezium.engine.ChangeEvent<String, String>> =
            DebeziumEngine.create<String>(io.debezium.engine.format.Json::class.java)
                .using(
                    getDebeziumProperties(
                        path,
                        listOf("$databaseName\\.$collectionName")
                            .stream()
                            .collect(Collectors.joining(","))
                    )
                )
                .using(io.debezium.engine.spi.OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
                .notifying { e: io.debezium.engine.ChangeEvent<String, String> ->
                    // debezium outputs a tombstone event that has a value of null. this is an
                    // artifact of how it
                    // interacts with kafka. we want to ignore it.
                    // more on the tombstone:
                    // https://debezium.io/documentation/reference/configuration/event-flattening.html
                    if (e.value() != null) {
                        LOGGER.info("{}", e)
                        var inserted = false
                        while (!inserted) {
                            inserted = queue.offer(e)
                        }
                    }
                }
                .using(
                    io.debezium.engine.DebeziumEngine.CompletionCallback {
                        success: Boolean,
                        message: String?,
                        error: Throwable? ->
                        LOGGER.info("Incremental snapshot Debezium engine shutdown.")
                        if (error != null) {
                            LOGGER.error("error occurred: {}", message, error)
                        }
                        engineLatch2.countDown()
                        thrownError2.set(error)
                    }
                )
                .build()
        executorService2.execute(engine2)
        Thread.sleep((180 * 1000).toLong())
        engine2.close()
        engineLatch2.await(5, TimeUnit.MINUTES)
        executorService2.shutdown()
        executorService2.awaitTermination(5, TimeUnit.MINUTES)
        readOffsetFile(path)
        if (thrownError2.get() != null) {
            throw RuntimeException(thrownError2.get())
        }
    }

    protected fun getDebeziumProperties(
        cdcOffsetFilePath: Path,
        collectionNames: String
    ): Properties {
        val props = Properties()
        LOGGER.info("Included collection names regular expression: '{}'.", collectionNames)
        props.setProperty("connector.class", MongoDbConnector::class.java.getName())
        props.setProperty("snapshot.mode", "initial")
        props.setProperty("name", databaseName.replace("_".toRegex(), "-"))
        props.setProperty("mongodb.connection.string", connectionString)
        props.setProperty("mongodb.connection.mode", "replica_set")
        props.setProperty("mongodb.user", username)
        props.setProperty("mongodb.password", password)
        props.setProperty("mongodb.authsource", "admin")
        props.setProperty("mongodb.ssl.enabled", "true")
        props.setProperty("topic.prefix", databaseName)
        props.setProperty("capture.mode", "change_streams_update_full")

        // Database/collection selection
        props.setProperty("collection.include.list", collectionNames)
        props.setProperty("database.include.list", databaseName)

        // Offset storage configuration
        props.setProperty(
            "offset.storage",
            "org.apache.kafka.connect.storage.FileOffsetBackingStore"
        )
        props.setProperty("offset.storage.file.filename", cdcOffsetFilePath.toString())
        props.setProperty("offset.flush.interval.ms", "1000")

        // Advanced properties
        props.setProperty("max.batch.size", "2048")
        props.setProperty("max.queue.size", "8192")

        // https://debezium.io/documentation/reference/configuration/avro.html
        props.setProperty("key.converter.schemas.enable", "false")
        props.setProperty("value.converter.schemas.enable", "false")

        // By default "decimal.handing.mode=precise" which caused returning this value as a binary.
        // The "double" type may cause a loss of precision, so set Debezium's config to store it as
        // a String
        // explicitly in its Kafka messages for more details see:
        // https://debezium.io/documentation/reference/1.4/connectors/postgresql.html#postgresql-decimal-types
        // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
        props.setProperty("decimal.handling.mode", "string")
        props.setProperty("errors.log.include.messages", "true")
        props.setProperty("errors.log.enable", "true")
        props.setProperty("heartbeat.interval.ms", "500")
        return props
    }

    private val path: Path
        get() {
            val cdcWorkingDir: Path =
                try {
                    Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset")
                } catch (e: IOException) {
                    throw RuntimeException(e)
                }
            return cdcWorkingDir.resolve("offset.txt")
        }

    @SuppressFBWarnings("OBJECT_DESERIALIZATION")
    private fun readOffsetFile(path: Path) {
        LOGGER.info("Reading contents of offset file '{}'...", path)
        try {
            ObjectInputStream(Files.newInputStream(path)).use { ois ->
                val raw = ois.readObject() as Map<ByteArray, ByteArray>
                raw.entries.forEach(
                    Consumer { (key, value): Map.Entry<ByteArray, ByteArray> ->
                        LOGGER.info(
                            "{}:{}",
                            String(ByteBuffer.wrap(key).array(), StandardCharsets.UTF_8),
                            String(ByteBuffer.wrap(value).array(), StandardCharsets.UTF_8)
                        )
                    }
                )
            }
        } catch (e: IOException) {
            LOGGER.error("Unable to read offset file '{}'.", path, e)
        } catch (e: ClassNotFoundException) {
            LOGGER.error("Unable to read offset file '{}'.", path, e)
        }
    }

    companion object {
        private val LOGGER = LoggerFactory.getLogger(DebeziumMongoDbConnectorTest::class.java)
        @Throws(IOException::class, InterruptedException::class)
        @JvmStatic
        fun main(args: Array<String>) {
            val parser = ArgParser("Debezium MongoDb Connector Test Harness")
            val connectionString by
                parser
                    .option(
                        ArgType.String,
                        fullName = "connection-string",
                        shortName = "cs",
                        description = "MongoDB Connection String"
                    )
                    .required()
            val databaseName by
                parser
                    .option(
                        ArgType.String,
                        fullName = "database-name",
                        shortName = "d",
                        description = "Database Name"
                    )
                    .required()
            val collectionName by
                parser
                    .option(
                        ArgType.String,
                        fullName = "collection-name",
                        shortName = "cn",
                        description = "Collection Name"
                    )
                    .required()
            val username by
                parser
                    .option(
                        ArgType.String,
                        fullName = "username",
                        shortName = "u",
                        description = "Username"
                    )
                    .required()

            parser.parse(args)

            println("Enter password: ")
            val password = readln()

            val debeziumEngineTest =
                DebeziumMongoDbConnectorTest(
                    connectionString,
                    databaseName,
                    collectionName,
                    username,
                    password
                )
            debeziumEngineTest.startTest()
        }
    }
}
