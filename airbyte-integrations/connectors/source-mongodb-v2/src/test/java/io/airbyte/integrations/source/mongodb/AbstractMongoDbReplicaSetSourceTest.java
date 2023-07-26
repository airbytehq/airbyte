package io.airbyte.integrations.source.mongodb;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.MongoException;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import dev.failsafe.Failsafe;
import dev.failsafe.RetryPolicy;
import org.apache.commons.lang3.RandomStringUtils;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.wait.strategy.Wait;

import java.net.InetAddress;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

public abstract class AbstractMongoDbReplicaSetSourceTest extends AbstractMongoDbSourceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(AbstractMongoDbReplicaSetSourceTest.class);

    private static final String MONGO_CONTAINER_COMMAND = "--bind_ip localhost,%s --replSet %s --port %d";
    private static final String MONGO_EXEC_COMMAND = "until %s --port %d --eval %s | grep ok | grep 1 > /dev/null 2>&1; do sleep 1;done";
    private static final String REPLICA_SET_CONFIG_FORMAT =
            """
            {_id:\\"%s\\",members:[{_id:0,host:\\"%s:%d\\"},{_id:1,host:\\"%s:%d\\"},{_id:2,host:\\"%s:%d\\"}]}""";

    private GenericContainer mongoDbContainer1;
    private String mongoDbContainerName1;
    private GenericContainer mongoDbContainer2;
    private String mongoDbContainerName2;
    private GenericContainer mongoDbContainer3;
    private String mongoDbContainerName3;
    private Integer mongoDbListenPort;
    private Network network;
    private String networkAlias;
    private String replicaSetId;

    private final RetryPolicy retryPolicy = RetryPolicy.builder()
            .handle(MongoException.class)
            .withDelay(Duration.ofSeconds(10))
            .withMaxRetries(3)
            .build();

    @Override
    protected void doSetup() throws Exception {
        LOGGER.info("Setting up MongoDB cluster...");

        // Generate object names with some additional random characters to avoid conflicts with
        // other tests during parallel execution by Gradle
        final String randomHash = RandomStringUtils.random(6, true, true);
        mongoDbContainerName1 = "mongo1_" + randomHash;
        mongoDbContainerName2 = "mongo2_" + randomHash;
        mongoDbContainerName3 = "mongo3_" + randomHash;
        networkAlias = "mongodb_network_" + randomHash;
        replicaSetId = "replica-set-" + randomHash;

        // Use the first binding port as the MongoDB listen port.  This is also the
        // port that will be exposed by each Docker container.
        mongoDbListenPort = getPortBindings().get(0);

        network = Network.newNetwork();

// Uncomment to enable container logging for debugging purposes
//        final Slf4jLogConsumer logConsumer = new Slf4jLogConsumer(LOGGER);

        mongoDbContainer1 = new GenericContainer("mongo:" + getMongoDbVersion())
// Uncomment to enable container logging for debugging purposes
//                .withLogConsumer(logConsumer)
                .withNetwork(network)
                .withNetworkAliases(networkAlias)
                .withExposedPorts(mongoDbListenPort)
                .withCreateContainerCmdModifier(new MongoContainerCmdConsumer(mongoDbContainerName1))
                .withCommand(String.format(MONGO_CONTAINER_COMMAND, mongoDbContainerName1, replicaSetId, mongoDbListenPort));
        mongoDbContainer2 = new GenericContainer("mongo:" + getMongoDbVersion())
// Uncomment to enable container logging for debugging purposes
//                .withLogConsumer(logConsumer)
                .withNetwork(network)
                .withNetworkAliases(networkAlias)
                .withExposedPorts(mongoDbListenPort)
                .withCreateContainerCmdModifier(new MongoContainerCmdConsumer(mongoDbContainerName2))
                .withCommand(String.format(MONGO_CONTAINER_COMMAND, mongoDbContainerName2, replicaSetId, mongoDbListenPort));
        mongoDbContainer3 = new GenericContainer("mongo:" + getMongoDbVersion())
// Uncomment to enable container logging for debugging purposes
//                .withLogConsumer(logConsumer)
                .withNetwork(network)
                .withNetworkAliases(networkAlias)
                .withExposedPorts(mongoDbListenPort)
                .withCreateContainerCmdModifier(new MongoContainerCmdConsumer(mongoDbContainerName3))
                .withCommand(String.format(MONGO_CONTAINER_COMMAND, mongoDbContainerName3, replicaSetId, mongoDbListenPort));

        mongoDbContainer1.setPortBindings(List.of(getPortBindings().get(0) + ":" + mongoDbListenPort));
        mongoDbContainer2.setPortBindings(List.of(getPortBindings().get(1) + ":" + mongoDbListenPort));
        mongoDbContainer3.setPortBindings(List.of(getPortBindings().get(2) + ":" + mongoDbListenPort));

        LOGGER.info("Starting MongoDB cluster containers...");
        mongoDbContainer1.start();
        mongoDbContainer2.start();
        mongoDbContainer3.start();

        LOGGER.info("Waiting for MongoDB cluster instances to be available...");
        mongoDbContainer1.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));
        mongoDbContainer2.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));
        mongoDbContainer3.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));

        LOGGER.info("Initializing replica set...");
        final String replicaSetConfigJson = buildReplicaSetConfig();
        LOGGER.info(mongoDbContainer1.execInContainer("/bin/bash", "-c",
                String.format(MONGO_EXEC_COMMAND,
                        getMongoCommand(),
                        mongoDbListenPort,
                        "\"rs.initiate(" + replicaSetConfigJson + ", { force: true })\"")).getStderr());
        LOGGER.info(mongoDbContainer1.execInContainer("/bin/bash", "-c",
                String.format(MONGO_EXEC_COMMAND,
                        getMongoCommand(),
                        mongoDbListenPort,
                        "\"printjson(rs.isMaster())\"")).getStderr());

        LOGGER.info("Seeding collection '{}.{}' with data...", getDatabaseName(), getCollectionName());
        try (final MongoClient client = createMongoClient(getDatabaseName())) {
            generateDataSet(client);
        }
    }

    @Override
    protected void doCleanup() {
        mongoDbContainer1.stop();
        mongoDbContainer2.stop();
        mongoDbContainer3.stop();

        network.close();
    }

    @Override
    protected void generateDataSet(final MongoClient client) {
        final MongoCollection<Document> collection = client.getDatabase(getDatabaseName()).getCollection(getCollectionName());
        final List<Document> documents = IntStream.range(0, getDataSetSize()).boxed()
                .map(i -> new Document().append("_id", new ObjectId())
                        .append("title", "Movie #" + i)
                        .append(getCursorField(), i))
                .collect(Collectors.toList());

        /*
         * Use a retry policy to avoid a race condition between the execution of this insert
         * and the setup and configuration of the replica set and network.
         */
        Failsafe.with(retryPolicy).run(() -> collection.insertMany(documents));
    }

    @Override
    protected Integer getFirstMappedPort() {
        return mongoDbContainer1.getFirstMappedPort();
    }

    @Override
    protected String getHost() {
        return mongoDbContainer1.getHost();
    }

    protected abstract List<Integer> getPortBindings();

    protected abstract String getMongoCommand();

    private String buildReplicaSetConfig() {
        return String.format(REPLICA_SET_CONFIG_FORMAT, replicaSetId,
                mongoDbContainerName1, mongoDbListenPort,
                mongoDbContainerName2, mongoDbListenPort,
                mongoDbContainerName3, mongoDbListenPort);
    }

    @Override
    protected String createConnectionString(final String databaseName) {
        final String connectionUrl = "mongodb://" +
                mongoDbContainerName1 + ":" + mongoDbContainer1.getMappedPort(mongoDbListenPort) +
                "," +
                mongoDbContainerName2 + ":" + mongoDbContainer2.getMappedPort(mongoDbListenPort) +
                "," +
                mongoDbContainerName3 + ":" + mongoDbContainer3.getMappedPort(mongoDbListenPort) +
                "/" + databaseName +
                "?retryWrites=false&replicaSet=" + replicaSetId;
        LOGGER.info("Created replica set URL: {}.", connectionUrl);
        return connectionUrl;
    }

    @Override
    protected List<String> getFieldNames() {
        return List.of("_id", "title", getCursorField());
    }
}
