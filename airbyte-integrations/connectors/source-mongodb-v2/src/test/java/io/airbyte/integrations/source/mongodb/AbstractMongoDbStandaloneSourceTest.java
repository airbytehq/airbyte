package io.airbyte.integrations.source.mongodb;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import org.apache.commons.lang3.RandomStringUtils;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.wait.strategy.Wait;

import java.io.IOException;
import java.sql.Timestamp;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public abstract class AbstractMongoDbStandaloneSourceTest extends AbstractMongoDbSourceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(AbstractMongoDbStandaloneSourceTest.class);

    private GenericContainer mongoDbContainer;
    private String mongoDbContainerName;
    private Network network;
    private String networkAlias;

    @Override
    protected void doSetup() throws IOException, InterruptedException {
        LOGGER.info("Setting up MongoDB standalone instance...");

        // Generate object names with some additional random characters to avoid conflicts with
        // other tests during parallel execution by Gradle
        final String randomHash = RandomStringUtils.random(6, true, true);
        mongoDbContainerName = "mongo_" + randomHash;
        networkAlias = "mongodb_network_" + randomHash;

        network = Network.newNetwork();

// Uncomment to enable container logging for debugging purposes
//        final Slf4jLogConsumer logConsumer = new Slf4jLogConsumer(LOGGER);

        mongoDbContainer = new GenericContainer("mongo:" + getMongoDbVersion())
// Uncomment to enable container logging for debugging purposes
//                .withLogConsumer(logConsumer)
                .withNetwork(network)
                .withNetworkAliases(networkAlias)
                .withExposedPorts(getListenPort())
                .withCommand("--bind_ip localhost," + mongoDbContainerName + " --port " + getListenPort())
                .withCreateContainerCmdModifier(new MongoContainerCmdConsumer(mongoDbContainerName));

        mongoDbContainer.setPortBindings(List.of(getListenPort() + ":" + getListenPort()));

        LOGGER.info("Starting MongoDB standalone container...");
        mongoDbContainer.start();

        LOGGER.info("Waiting for MongoDB standalone instance to be available...");
        mongoDbContainer.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));

        LOGGER.info("Seeding collection '{}.{}' with data...", getDatabaseName(), getCollectionName());
        try (final MongoClient client = createMongoClient(getDatabaseName())) {
            generateDataSet(client);
        }
    }

    @Override
    protected void doCleanup() {
        mongoDbContainer.stop();
    }

    @Override
    protected void generateDataSet(final MongoClient client) {
        final MongoCollection<Document> collection = client.getDatabase(getDatabaseName()).getCollection(getCollectionName());
        final List<Document> documents = IntStream.range(0, getDataSetSize()).boxed()
                .map(this::buildDocument).collect(Collectors.toList());
        collection.insertMany(documents);
    }

    @Override
    protected Integer getFirstMappedPort() {
        return mongoDbContainer.getFirstMappedPort();
    }

    @Override
    protected String getHost() {
        return mongoDbContainer.getHost();
    }

    protected abstract Integer getListenPort();

    private Document buildDocument(final Integer i) {
        return new Document().append("_id", new ObjectId())
                .append("title", "Movie #" + i)
                .append(getCursorField(), i)
                .append("timestamp", new Timestamp(System.currentTimeMillis())
                        .toString().replace(' ', 'T'));
    }

    @Override
    protected String createConnectionString(final String databaseName) {
        final String connectionString = "mongodb://" +
                mongoDbContainerName +
                ":" +
                mongoDbContainer.getMappedPort(getListenPort()) +
                "/" +
                databaseName +
                "?retryWrites=false";
        LOGGER.info("Created connection string: {}.", connectionString);
        return connectionString;
    }

    @Override
    protected List<String> getFieldNames() {
        return List.of("_id", "title", getCursorField(), "timestamp");
    }
}
