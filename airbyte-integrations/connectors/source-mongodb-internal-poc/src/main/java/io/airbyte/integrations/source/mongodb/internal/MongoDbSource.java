/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

  /**
   * Set of collection prefixes that should be ignored when performing operations, such as discover to
   * avoid access issues.
   */
  private static final Set<String> IGNORED_COLLECTIONS = Set.of("system.", "replset.", "oplog.");

  public static void main(final String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config)) {
      final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();

      /*
       * Perform the authorized collections check before the cluster type check. The MongoDB Java driver
       * needs to actually execute a command in order to fetch the cluster description. Querying for the
       * authorized collections guarantees that the cluster description will be available to the driver.
       */
      if (getAuthorizedCollections(mongoClient, databaseName).isEmpty()) {
        return new AirbyteConnectionStatus()
            .withMessage("Target MongoDB database does not contain any authorized collections.")
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      }
      if (!ClusterType.REPLICA_SET.equals(mongoClient.getClusterDescription().getType())) {
        return new AirbyteConnectionStatus()
            .withMessage("Target MongoDB instance is not a replica set cluster.")
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform source check operation.", e);
      return new AirbyteConnectionStatus()
          .withMessage(e.getMessage())
          .withStatus(AirbyteConnectionStatus.Status.FAILED);
    }

    LOGGER.info("The source passed the check operation test!");
    return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    final List<AirbyteStream> streams = discoverInternal(config);
    return new AirbyteCatalog().withStreams(streams);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    return null;
  }

  private Set<String> getAuthorizedCollections(final MongoClient mongoClient, final String databaseName) {
    /*
     * db.runCommand ({listCollections: 1.0, authorizedCollections: true, nameOnly: true }) the command
     * returns only those collections for which the user has privileges. For example, if a user has find
     * action on specific collections, the command returns only those collections; or, if a user has
     * find or any other action, on the database resource, the command lists all collections in the
     * database.
     */
    try {
      final Document document = mongoClient.getDatabase(databaseName).runCommand(new Document("listCollections", 1)
          .append("authorizedCollections", true)
          .append("nameOnly", true))
          .append("filter", "{ 'type': 'collection' }");
      return document.toBsonDocument()
          .get("cursor").asDocument()
          .getArray("firstBatch")
          .stream()
          .map(bsonValue -> bsonValue.asDocument().getString("name").getValue())
          .filter(this::isSupportedCollection)
          .collect(Collectors.toSet());
    } catch (final MongoSecurityException e) {
      final MongoCommandException exception = (MongoCommandException) e.getCause();
      throw new ConnectionErrorException(String.valueOf(exception.getCode()), e);
    } catch (final MongoException e) {
      throw new ConnectionErrorException(String.valueOf(e.getCode()), e);
    }
  }

  private List<AirbyteStream> discoverInternal(final JsonNode config) {
    final List<AirbyteStream> streams = new ArrayList<>();
    try (final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config)) {
      final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
      final Set<String> authorizedCollections = getAuthorizedCollections(mongoClient, databaseName);
      authorizedCollections.parallelStream().forEach(collectionName -> {
        final List<Field> fields = getFields(mongoClient.getDatabase(databaseName).getCollection(collectionName));
        streams.add(CatalogHelpers.createAirbyteStream(collectionName, "", fields));
      });
      return streams;
    }
  }

  private List<Field> getFields(final MongoCollection collection) {
    final Map<String, Object> fieldsMap = Map.of("input", Map.of("$objectToArray", "$$ROOT"),
        "as", "each",
        "in", Map.of("k", "$$each.k", "v", Map.of("$type", "$$each.v")));

    final Document mapFunction = new Document("$map", fieldsMap);
    final Document arrayToObjectAggregation = new Document("$arrayToObject", mapFunction);
    final Document projection = new Document("$project", new Document("fields", arrayToObjectAggregation));

    final Map<String, Object> groupMap = new HashMap<>();
    groupMap.put("_id", null);
    groupMap.put("fields", Map.of("$addToSet", "$fields"));

    final AggregateIterable<Document> output = collection.aggregate(Arrays.asList(
        projection,
        new Document("$unwind", "$fields"),
        new Document("$group", groupMap)));

    final MongoCursor<Document> cursor = output.cursor();
    if (cursor.hasNext()) {
      final Map<String, String> fields = ((List<Map<String, String>>) output.cursor().next().get("fields")).get(0);
      return fields.entrySet().stream()
          .map(e -> new Field(e.getKey(), convertToSchemaType(e.getValue())))
          .collect(Collectors.toList());
    } else {
      return List.of();
    }
  }

  private JsonSchemaType convertToSchemaType(final String type) {
    return switch (type) {
      case "boolean" -> JsonSchemaType.BOOLEAN;
      case "int", "long", "double", "decimal" -> JsonSchemaType.NUMBER;
      case "array" -> JsonSchemaType.ARRAY;
      case "object", "javascriptWithScope" -> JsonSchemaType.OBJECT;
      default -> JsonSchemaType.STRING;
    };
  }

  private boolean isSupportedCollection(final String collectionName) {
    return !IGNORED_COLLECTIONS.stream().anyMatch(s -> collectionName.startsWith(s));
  }

}
