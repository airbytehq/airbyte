/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Aggregates;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.OptionalInt;
import java.util.Set;
import java.util.stream.Collectors;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtil.class);

  /**
   * The maximum number of documents to sample when attempting to discover the unique keys/types for a
   * collection. Inspired by the
   * <a href="https://www.mongodb.com/docs/compass/current/sampling/#sampling-method">sampling method
   * utilized by the MongoDB Compass client</a>.
   */
  private static final Integer DISCOVERY_SAMPLE_SIZE = 1000;

  /**
   * Set of collection prefixes that should be ignored when performing operations, such as discover to
   * avoid access issues.
   */
  private static final Set<String> IGNORED_COLLECTIONS = Set.of("system.", "replset.", "oplog.");

  /**
   * The minimum size of the Debezium event queue. This value will be selected if the provided
   * configuration value for the queue size is less than this value
   */
  @VisibleForTesting
  static final int MIN_QUEUE_SIZE = 1000;

  /**
   * The maximum size of the Debezium event queue. This value will be selected if the provided
   * configuration value for the queue size is greater than this value OR if no value is provided.
   */
  @VisibleForTesting
  static final int MAX_QUEUE_SIZE = 10000;

  /**
   * Returns the set of collections that the current credentials are authorized to access.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server for authorized
   *        collections.
   * @param databaseName The name of the database to query for authorized collections.
   * @return The set of authorized collection names (may be empty).
   * @throws ConnectionErrorException if unable to perform the authorized collection query.
   */
  public static Set<String> getAuthorizedCollections(final MongoClient mongoClient, final String databaseName) {
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
          .filter(MongoUtil::isSupportedCollection)
          .collect(Collectors.toSet());
    } catch (final MongoSecurityException e) {
      final MongoCommandException exception = (MongoCommandException) e.getCause();
      throw new ConnectionErrorException(String.valueOf(exception.getCode()), e);
    } catch (final MongoException e) {
      throw new ConnectionErrorException(String.valueOf(e.getCode()), e);
    }
  }

  /**
   * Retrieves the {@link AirbyteStream}s available to the source by querying the MongoDB server.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param databaseName The name of the database to query for collections.
   * @return The list of {@link AirbyteStream}s that map to the available collections in the provided
   *         database.
   */
  public static List<AirbyteStream> getAirbyteStreams(final MongoClient mongoClient, final String databaseName) {
    final Set<String> authorizedCollections = getAuthorizedCollections(mongoClient, databaseName);
    return authorizedCollections.parallelStream().map(collectionName -> {
      /*
       * Fetch the keys/types from the first N documents and the last N documents from the collection.
       * This is an attempt to "survey" the documents in the collection for variance in the schema keys.
       */
      final MongoCollection<Document> mongoCollection = mongoClient.getDatabase(databaseName).getCollection(collectionName);
      final Set<Field> discoveredFields = new HashSet<>(getFieldsInCollection(mongoCollection));
      return createAirbyteStream(collectionName, databaseName, new ArrayList<>(discoveredFields));
    }).collect(Collectors.toList());
  }

  /**
   * Computes the size of the queue that will contain events generated by Debezium. If a queue size
   * value is provided as part of the source's configuration, this method guarantees that the selected
   * queue size is within the {@link #MIN_QUEUE_SIZE} and {@link #MAX_QUEUE_SIZE} values. If the value
   * is not present in the configuration, the {@link #MAX_QUEUE_SIZE} is selected.
   *
   * @param config The source connector's configuration.
   * @return The size of the Debezium event queue.
   */
  public static OptionalInt getDebeziumEventQueueSize(final JsonNode config) {
    final OptionalInt sizeFromConfig =
        config.has(QUEUE_SIZE_CONFIGURATION_KEY) ? OptionalInt.of(config.get(QUEUE_SIZE_CONFIGURATION_KEY).asInt()) : OptionalInt.empty();

    if (sizeFromConfig.isPresent()) {
      int size = sizeFromConfig.getAsInt();
      if (size < MIN_QUEUE_SIZE) {
        LOGGER.warn("Queue size is overridden to {} , which is the min allowed for safety.",
            MIN_QUEUE_SIZE);
        return OptionalInt.of(MIN_QUEUE_SIZE);
      } else if (size > MAX_QUEUE_SIZE) {
        LOGGER.warn("Queue size is overridden to {} , which is the max allowed for safety.",
            MAX_QUEUE_SIZE);
        return OptionalInt.of(MAX_QUEUE_SIZE);
      }
      return OptionalInt.of(size);
    }
    return OptionalInt.of(MAX_QUEUE_SIZE);
  }

  private static AirbyteStream createAirbyteStream(final String collectionName, final String databaseName, final List<Field> fields) {
    return MongoCatalogHelper.buildAirbyteStream(collectionName, databaseName, fields);
  }

  private static Set<Field> getFieldsInCollection(final MongoCollection<Document> collection) {
    final Set<Field> discoveredFields = new HashSet<>();
    final Map<String, Object> fieldsMap = Map.of("input", Map.of("$objectToArray", "$$ROOT"),
        "as", "each",
        "in", Map.of("k", "$$each.k", "v", Map.of("$type", "$$each.v")));

    final Document mapFunction = new Document("$map", fieldsMap);
    final Document arrayToObjectAggregation = new Document("$arrayToObject", mapFunction);

    final Map<String, Object> groupMap = new HashMap<>();
    groupMap.put("_id", null);
    groupMap.put("fields", Map.of("$addToSet", "$fields"));

    final List<Bson> aggregateList = new ArrayList<>();
    aggregateList.add(Aggregates.sample(DISCOVERY_SAMPLE_SIZE));
    aggregateList.add(Aggregates.project(new Document("fields", arrayToObjectAggregation)));
    aggregateList.add(Aggregates.unwind("$fields"));
    aggregateList.add(new Document("$group", groupMap));

    final AggregateIterable<Document> output = collection.aggregate(aggregateList);

    try (final MongoCursor<Document> cursor = output.cursor()) {
      while (cursor.hasNext()) {
        final Map<String, String> fields = ((List<Map<String, String>>) cursor.next().get("fields")).get(0);
        discoveredFields.addAll(fields.entrySet().stream()
            .map(e -> new MongoField(e.getKey(), convertToSchemaType(e.getValue())))
            .collect(Collectors.toSet()));
      }
    }

    return discoveredFields;
  }

  private static JsonSchemaType convertToSchemaType(final String type) {
    return switch (type) {
      case "boolean" -> JsonSchemaType.BOOLEAN;
      case "int", "long", "double", "decimal" -> JsonSchemaType.NUMBER;
      case "array" -> JsonSchemaType.ARRAY;
      case "object", "javascriptWithScope" -> JsonSchemaType.OBJECT;
      default -> JsonSchemaType.STRING;
    };
  }

  private static boolean isSupportedCollection(final String collectionName) {
    return IGNORED_COLLECTIONS.stream().noneMatch(collectionName::startsWith);
  }

}
