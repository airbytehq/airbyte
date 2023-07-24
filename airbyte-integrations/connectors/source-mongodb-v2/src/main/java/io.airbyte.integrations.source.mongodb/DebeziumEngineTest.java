package io.airbyte.integrations.source.mongodb;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.ReadPreference;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.debezium.connector.mongodb.MongoDbConnector;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import io.debezium.engine.spi.OffsetCommitPolicy.AlwaysCommitOffsetPolicy;
import org.bson.BsonDocument;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

public class DebeziumEngineTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumEngineTest.class);

    public static final String COLLECTION_NAME = "listingsAndReviews";
    public static final String DATABASE_NAME = "sample_airbnb";
    public static final List<String> COLLECTIONS = List.of(DATABASE_NAME + "\\." + COLLECTION_NAME);

    private final String username;

    private final String password;

    DebeziumEngineTest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public static void main(final String[] args) throws IOException, InterruptedException {
        if (args.length < 2) {
            LOGGER.error("Must provide <username> and <password> arguments!");
            System.exit(-1);
        }

        final DebeziumEngineTest debeziumEngineTest = new DebeziumEngineTest(args[0], args[1]);
        debeziumEngineTest.startTest();
    }

    public void startTest() throws InterruptedException, IOException {
        final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(10_000);
        final Path path = getPath();

        LOGGER.info("Using offset storage path '{}'.", path);

        testChangeEventStream();

        //will do an initial sync cause offset is null
        initialSync(queue, path);
//
//        // will do an incremental processing cause after the initialSync run the offset must be updated
//        engineWithIncrementalSnapshot(queue, path);

    }

    private void testChangeEventStream() {

        final MongoClientSettings mongoClientSettings = MongoClientSettings.builder()
                .applyConnectionString(new ConnectionString("mongodb+srv://" + getUsername() + ":" + getPassword() + "@cluster0.iqgf8.mongodb.net/"))
                .readPreference(ReadPreference.secondaryPreferred())
                .build();
        try (final MongoClient client = MongoClients.create(mongoClientSettings)) {
            LOGGER.info("Retrieving change stream...");
            ChangeStreamIterable<BsonDocument> stream = client.watch(BsonDocument.class);
            LOGGER.info("Retrieving cursor...");
            MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> changeStreamCursor = stream.cursor();

            /*
             * Must call tryNext before attempting to get the resume token from the cursor directly.
             * Otherwise, both will return null!
             */
            final ChangeStreamDocument<BsonDocument> cursorDocument = changeStreamCursor.tryNext();
            if(cursorDocument != null) {
                LOGGER.info("Resume token from cursor document: {}", cursorDocument.getResumeToken());
            } else  {
                LOGGER.info("Cursor document is null.");
            }
            LOGGER.info("Resume token = {}", changeStreamCursor.getResumeToken());
        }
    }

    private void initialSync(LinkedBlockingQueue<ChangeEvent<String, String>> queue, Path path) throws InterruptedException, IOException {
        final ExecutorService executorService = Executors.newSingleThreadExecutor();
        final AtomicReference<Throwable> thrownError = new AtomicReference<>();
        final CountDownLatch engineLatch = new CountDownLatch(1);

        final DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
                .using(getDebeziumProperties(path, COLLECTIONS.stream().collect(Collectors.joining(","))))
                .using(new AlwaysCommitOffsetPolicy())
                .notifying(e -> {
                    // debezium outputs a tombstone event that has a value of null. this is an artifact of how it
                    // interacts with kafka. we want to ignore it.
                    // more on the tombstone:
                    // https://debezium.io/documentation/reference/configuration/event-flattening.html
                    if (e.value() != null) {
                        LOGGER.debug("{}", e);
                        boolean inserted = false;
                        while (!inserted) {
                            inserted = queue.offer(e);
                        }
                    }
                })
                .using((success, message, error) -> {
                    LOGGER.info("Initial sync Debezium engine shutdown.");
                    if (error != null) {
                        LOGGER.error("error occurred: {}", message, error);
                    }
                    engineLatch.countDown();
                    thrownError.set(error);
                })
                .build();

        executorService.execute(engine);

        Thread.sleep(45 * 1000);

        engine.close();
        engineLatch.await(5, TimeUnit.MINUTES);
        executorService.shutdown();
        executorService.awaitTermination(5, TimeUnit.MINUTES);

        readOffsetFile(path);

        if (thrownError.get() != null) {
            throw new RuntimeException(thrownError.get());
        }
    }

    private void engineWithIncrementalSnapshot(LinkedBlockingQueue<ChangeEvent<String, String>> queue, Path path)
            throws InterruptedException, IOException {
        final ExecutorService executorService2 = Executors.newSingleThreadExecutor();
        final AtomicReference<Throwable> thrownError2 = new AtomicReference<>();
        final CountDownLatch engineLatch2 = new CountDownLatch(1);
        final DebeziumEngine<ChangeEvent<String, String>> engine2 = DebeziumEngine.create(Json.class)
                .using(getDebeziumProperties(path, COLLECTIONS.stream().collect(Collectors.joining(","))))
                .using(new AlwaysCommitOffsetPolicy())
                .notifying(e -> {
                    // debezium outputs a tombstone event that has a value of null. this is an artifact of how it
                    // interacts with kafka. we want to ignore it.
                    // more on the tombstone:
                    // https://debezium.io/documentation/reference/configuration/event-flattening.html
                    if (e.value() != null) {
                        LOGGER.debug("{}", e);
                        boolean inserted = false;
                        while (!inserted) {
                            inserted = queue.offer(e);
                        }
                    }
                })
                .using((success, message, error) -> {
                    LOGGER.info("Incremental snapshot Debezium engine shutdown.");
                    if (error != null) {
                        LOGGER.error("error occurred: {}", message, error);
                    }
                    engineLatch2.countDown();
                    thrownError2.set(error);
                })
                .build();

        executorService2.execute(engine2);
        Thread.sleep(180 * 1000);

        engine2.close();
        engineLatch2.await(5, TimeUnit.MINUTES);
        executorService2.shutdown();
        executorService2.awaitTermination(5, TimeUnit.MINUTES);

        readOffsetFile(path);

        if (thrownError2.get() != null) {
            throw new RuntimeException(thrownError2.get());
        }
    }

    protected Properties getDebeziumProperties(final Path cdcOffsetFilePath, final String collectionNames) {
        final Properties props = new Properties();

        LOGGER.info("Included collection names regular expression: '{}'.", collectionNames);

        props.setProperty("connector.class", MongoDbConnector.class.getName());
        props.setProperty("snapshot.mode", "initial");

        props.setProperty("name", DATABASE_NAME.replaceAll("_", "-"));

        props.setProperty("mongodb.connection.string", "mongodb+srv://cluster0.iqgf8.mongodb.net/"); //?replicaSet=atlas-pexnnq-shard-0");
        props.setProperty("mongodb.connection.mode", "replica_set");
        props.setProperty("mongodb.user", getUsername());
        props.setProperty("mongodb.password", getPassword());
        props.setProperty("mongodb.authsource", "admin");
        props.setProperty("topic.prefix", DATABASE_NAME);
        props.setProperty("capture.mode", "change_streams_update_full");

        // Database/collection selection
        props.setProperty("collection.include.list", collectionNames);
        props.setProperty("database.include.list", DATABASE_NAME);

        // Offset storage configuration
        props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
        props.setProperty("offset.storage.file.filename", cdcOffsetFilePath.toString());
        props.setProperty("offset.flush.interval.ms", "1000");

        // Advanced properties
        props.setProperty("max.batch.size", "2048");
        props.setProperty("max.queue.size", "8192");

        // https://debezium.io/documentation/reference/configuration/avro.html
        props.setProperty("key.converter.schemas.enable", "false");
        props.setProperty("value.converter.schemas.enable", "false");

        // By default "decimal.handing.mode=precise" which caused returning this value as a binary.
        // The "double" type may cause a loss of precision, so set Debezium's config to store it as a String
        // explicitly in its Kafka messages for more details see:
        // https://debezium.io/documentation/reference/1.4/connectors/postgresql.html#postgresql-decimal-types
        // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
        props.setProperty("decimal.handling.mode", "string");

        props.setProperty("errors.log.include.messages", "true");
        props.setProperty("errors.log.enable", "true");

        return props;
    }

    private Path getPath() {
        final Path cdcWorkingDir;
        try {
            cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset");
        } catch (final IOException e) {
            throw new RuntimeException(e);
        }
        final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.txt");
        return cdcOffsetFilePath;
    }

    private void readOffsetFile(final Path path) {
        LOGGER.info("Reading contents of offset file '{}'...", path);
        try (ObjectInputStream ois = new ObjectInputStream(Files.newInputStream(path))) {
            final Object obj = ois.readObject();
            final Map<byte[], byte[]> raw = (Map<byte[], byte[]>) obj;
            raw.entrySet().forEach(e -> LOGGER.info("{}:{}",
                    new String(ByteBuffer.wrap(e.getKey()).array(), StandardCharsets.UTF_8),
                    new String(ByteBuffer.wrap(e.getValue()).array(), StandardCharsets.UTF_8)));
        } catch (IOException | ClassNotFoundException e) {
            LOGGER.error("Unable to read offset file '{}'.", path, e);
        }
    }
}
