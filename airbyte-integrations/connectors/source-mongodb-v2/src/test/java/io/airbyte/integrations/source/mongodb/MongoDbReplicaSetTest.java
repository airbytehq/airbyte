/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.github.dockerjava.api.command.CreateContainerCmd;
import com.mongodb.ConnectionString;
import com.mongodb.CursorType;
import com.mongodb.MongoClientSettings;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Updates;
import java.io.IOException;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.bson.BsonTimestamp;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.containers.output.Slf4jLogConsumer;
import org.testcontainers.containers.wait.strategy.Wait;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class MongoDbReplicaSetTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbReplicaSetTest.class);

  private static final String COLLECTION_NAME = "movies";
  private static final String DB_NAME = "airbyte_test";
  private static final Integer DATASET_SIZE = 10000;
  private static final String LOCAL_DB_NAME = "local";
  private static final String MONGO_DB_IMAGE_TAG = "mongo:6.0.8";
  private static final String MONGO_DB1_NAME = "mongo1";
  private static final String MONGO_DB2_NAME = "mongo2";
  private static final String MONGO_DB3_NAME = "mongo3";
  private static final Integer MONGO_DB_PORT = 27017;
  private static final String MONGO_NETWORK = "mongodb_network";
  private static final String OPLOG = "oplog.rs";
  private static final String REPLICA_SET_ID = "replica-set";
  private static final String REPLICA_SET_CONFIG_FORMAT =
      """
      {_id:\\"%s\\",members:[{_id:0,host:\\"%s\\"},{_id:1,host:\\"%s\\"},{_id:2,host:\\"%s\\"}]}""";

  private static Network network;
  private static GenericContainer MONGO_DB1;
  private static GenericContainer MONGO_DB2;
  private static GenericContainer MONGO_DB3;

  @BeforeAll
  static void init() throws IOException, InterruptedException {
    final Slf4jLogConsumer logConsumer = new Slf4jLogConsumer(LOGGER);
    LOGGER.info("Setting up MongoDB cluster...");

    network = Network.newNetwork();

    MONGO_DB1 = new GenericContainer(MONGO_DB_IMAGE_TAG)
        .withNetwork(network)
        .withNetworkAliases(MONGO_NETWORK)
        .withExposedPorts(MONGO_DB_PORT)
        .withCreateContainerCmdModifier(new MongoContainerConsumer(MONGO_DB1_NAME))
        .withCommand("--bind_ip localhost," + MONGO_DB1_NAME + " --replSet " + REPLICA_SET_ID)
        .withLogConsumer(logConsumer);
    MONGO_DB2 = new GenericContainer(MONGO_DB_IMAGE_TAG)
        .withNetwork(network)
        .withNetworkAliases(MONGO_NETWORK)
        .withExposedPorts(MONGO_DB_PORT)
        .withCreateContainerCmdModifier(new MongoContainerConsumer(MONGO_DB2_NAME))
        .withCommand("--bind_ip localhost," + MONGO_DB2_NAME + " --replSet " + REPLICA_SET_ID)
        .withLogConsumer(logConsumer);
    MONGO_DB3 = new GenericContainer(MONGO_DB_IMAGE_TAG)
        .withNetwork(network)
        .withNetworkAliases(MONGO_NETWORK)
        .withExposedPorts(MONGO_DB_PORT)
        .withCreateContainerCmdModifier(new MongoContainerConsumer(MONGO_DB3_NAME))
        .withCommand("--bind_ip localhost," + MONGO_DB3_NAME + " --replSet " + REPLICA_SET_ID)
        .withLogConsumer(logConsumer);

    MONGO_DB1.setPortBindings(List.of("27017:" + MONGO_DB_PORT));
    MONGO_DB2.setPortBindings(List.of("27018:" + MONGO_DB_PORT));
    MONGO_DB3.setPortBindings(List.of("27019:" + MONGO_DB_PORT));

    LOGGER.info("Starting MongoDB containers...");
    MONGO_DB1.start();
    MONGO_DB2.start();
    MONGO_DB3.start();

    LOGGER.info("Waiting for MongoDB instances to be available...");
    MONGO_DB1.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));
    MONGO_DB2.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));
    MONGO_DB3.waitingFor(Wait.forLogMessage("(?i).*waiting for connections.*", 1));

    LOGGER.info("Initializing replica set...");
    final String replicaSetConfigJson = buildReplicaSetConfig();
    LOGGER.info("********* {}", replicaSetConfigJson);
    LOGGER.info(MONGO_DB1.execInContainer("/bin/bash", "-c",
        "mongosh --eval \"rs.initiate(" + replicaSetConfigJson + ", { force: true })\"").getStderr());
    LOGGER.info(MONGO_DB1.execInContainer("/bin/bash", "-c",
        "mongosh --eval \"rs.status()\"").getStderr());

    LOGGER.info("Seeding collection with data...");
    try (final MongoClient client = createMongoClient(DB_NAME)) {
      final MongoCollection<Document> collection = client.getDatabase(DB_NAME).getCollection(COLLECTION_NAME);
      final List<Document> documents = IntStream.range(0, DATASET_SIZE).boxed()
          .map(i -> new Document().append("_id", new ObjectId()).append("title", "Movie #" + i).append("catalogId", i))
          .collect(Collectors.toList());
      collection.insertMany(documents);
    }

    LOGGER.info("Setup complete.");
  }

  @AfterAll
  static void cleanup() {
    MONGO_DB1.stop();
    MONGO_DB2.stop();
    MONGO_DB3.stop();

    network.close();
  }

  @Test
  @Order(Integer.MIN_VALUE)
  void testOplogContainsAllCollectionData() {
    try (final MongoClient client = createMongoClient(DB_NAME)) {
      final MongoCollection<Document> oplog = client.getDatabase(LOCAL_DB_NAME).getCollection(OPLOG);
      final Document filter = new Document();
      filter.put("ns", DB_NAME + "." + COLLECTION_NAME);
      filter.put("op", new Document("$in", Arrays.asList("i", "u", "d")));
      final Document projection = new Document("ts", 1).append("op", 1).append("o", 1);
      final Document sort = new Document("$natural", 1);

      final MongoCursor<Document> cursor = oplog
          .find(filter)
          .projection(projection)
          .sort(sort)
          .cursorType(CursorType.TailableAwait)
          .noCursorTimeout(true)
          .cursor();

      final Collection<Document> changes = new ArrayList<>();

      while (true) {
        final Document document = cursor.tryNext();
        if (document == null) {
          break;
        } else {
          changes.add(document);
        }
      }

      assertEquals(DATASET_SIZE, changes.size());
    }
  }

  @Test
  @Order(Integer.MAX_VALUE)
  void testCollectionModificationsInOplog() {
    final String insertedTitle = "Movie #AAA";
    final String updatedTitle = "foo";

    // Record the current time for use in the oplog filter
    final int now = Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue();

    try (final MongoClient client = createMongoClient(DB_NAME)) {
      final MongoCollection<Document> oplog = client.getDatabase(LOCAL_DB_NAME).getCollection(OPLOG);
      final MongoCollection<Document> movieCollection = client.getDatabase(DB_NAME).getCollection(COLLECTION_NAME);

      // Insert a new document
      movieCollection.insertOne(new Document().append("_id", new ObjectId())
          .append("title", insertedTitle).append("catalogId", DATASET_SIZE + 1));

      // Update an existing document
      final Document updateQuery = new Document();
      updateQuery.append("catalogId", new Document("$eq", 1234));
      movieCollection.updateOne(updateQuery, Updates.set("title", updatedTitle));

      // Delete an existing document
      final Bson deleteQuery = Filters.eq("catalogId", 999);
      final Document deletedDocument = movieCollection.findOneAndDelete(deleteQuery);

      final Document filter = new Document();
      filter.put("ns", DB_NAME + "." + COLLECTION_NAME);
      filter.put("op", new Document("$in", Arrays.asList("i", "u", "d")));
      filter.put("ts", new Document().append("$gte", new BsonTimestamp(now, 1)));
      final Document projection = new Document("ts", 1).append("op", 1).append("o", 1);
      final Document sort = new Document("$natural", 1);

      final MongoCursor<Document> cursor = oplog
          .find(filter)
          .projection(projection)
          .sort(sort)
          .cursorType(CursorType.TailableAwait)
          .noCursorTimeout(true)
          .cursor();

      final Collection<Document> changes = new ArrayList<>();

      while (true) {
        final Document document = cursor.tryNext();
        if (document == null) {
          break;
        } else {
          LOGGER.info("{}", document);
          changes.add(document);
        }
      }

      assertEquals(3, changes.size());

      assertTrue(changes.stream().filter(d -> "i".equals(d.get("op"))).findFirst().isPresent());
      final Document insertedDocument = (Document) changes.stream().filter(d -> "i".equals(d.get("op"))).findFirst().get().get("o");
      assertEquals(insertedTitle, insertedDocument.get("title"));

      assertTrue(changes.stream().filter(d -> "u".equals(d.get("op"))).findFirst().isPresent());
      final Document updatedDocument = (Document) changes.stream().filter(d -> "u".equals(d.get("op"))).findFirst().get().get("o");
      final Document updatedDiff = ((Document) ((Document) updatedDocument.get("diff")).get("u"));
      assertEquals(updatedTitle, updatedDiff.get("title"));

      assertTrue(changes.stream().filter(d -> "d".equals(d.get("op"))).findFirst().isPresent());
      final Document deletedDocumentOpLog = (Document) changes.stream().filter(d -> "d".equals(d.get("op"))).findFirst().get().get("o");
      assertEquals(deletedDocument.get("_id"), deletedDocumentOpLog.get("_id"));
    }
  }

  private static String buildReplicaSetConfig() {
    return String.format(REPLICA_SET_CONFIG_FORMAT, REPLICA_SET_ID, MONGO_DB1_NAME, MONGO_DB2_NAME, MONGO_DB3_NAME);
  }

  private static MongoClient createMongoClient(final String databaseName) {
    return MongoClients.create(MongoClientSettings
        .builder()
        .applyConnectionString(new ConnectionString(createConnectionUrl(DB_NAME)))
        .inetAddressResolver(host -> List.of(InetAddress.getLocalHost()))
        .build());
  }

  private static String createConnectionUrl(final String databaseName) {
    final String connectionUrl = "mongodb://" +
        MONGO_DB1_NAME + ":" + MONGO_DB1.getMappedPort(MONGO_DB_PORT) +
        "," +
        MONGO_DB2_NAME + ":" + MONGO_DB2.getMappedPort(MONGO_DB_PORT) +
        "," +
        MONGO_DB3_NAME + ":" + MONGO_DB3.getMappedPort(MONGO_DB_PORT) +
        "/" + databaseName +
        "?retryWrites=false&replicaSet=" + REPLICA_SET_ID;
    LOGGER.info("Created replica set URL: {}.", connectionUrl);
    return connectionUrl;
  }

  private record MongoContainerConsumer(String name) implements Consumer<CreateContainerCmd> {

    @Override
    public void accept(final CreateContainerCmd createContainerCmd) {
      LOGGER.info("Setting name and hostname to {}...", name);
      createContainerCmd.withName(name).withHostName(name);
    }

  }

}
