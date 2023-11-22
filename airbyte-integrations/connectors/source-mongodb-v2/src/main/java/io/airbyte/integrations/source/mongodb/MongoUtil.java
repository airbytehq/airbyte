/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoIterable;
import com.mongodb.client.model.Aggregates;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtil.class);

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
   * Tests whether the database exists in target MongoDB instance.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server for the database
   *        names.
   * @param databaseName The database name from the source's configuration.
   * @return {@code true} if the database exists, {@code false} otherwise.
   */
  public static boolean checkDatabaseExists(final MongoClient mongoClient, final String databaseName) {
    final MongoIterable<String> databaseNames = mongoClient.listDatabaseNames();
    return StreamSupport.stream(databaseNames.spliterator(), false)
        .anyMatch(name -> name.equalsIgnoreCase(databaseName));
  }

  /**
   * Returns the set of collections that the current credentials are authorized to access.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server for authorized
   *        collections.
   * @param databaseName The name of the database to query for authorized collections.
   * @return The set of authorized collection names (may be empty).
   */
  public static Set<String> getAuthorizedCollections(final MongoClient mongoClient, final String databaseName) {
    /*
     * db.runCommand ({listCollections: 1.0, authorizedCollections: true, nameOnly: true }) the command
     * returns only those collections for which the user has privileges. For example, if a user has find
     * action on specific collections, the command returns only those collections; or, if a user has
     * find or any other action, on the database resource, the command lists all collections in the
     * database.
     */
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
  }

  /**
   * Retrieves the {@link AirbyteStream}s available to the source by querying the MongoDB server.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param databaseName The name of the database to query for collections.
   * @param sampleSize The maximum number of documents to sample when attempting to discover the
   *        unique fields for a collection.
   * @return The list of {@link AirbyteStream}s that map to the available collections in the provided
   *         database.
   */
  public static List<AirbyteStream> getAirbyteStreams(final MongoClient mongoClient, final String databaseName, final Integer sampleSize) {
    final Set<String> authorizedCollections = getAuthorizedCollections(mongoClient, databaseName);
    return authorizedCollections.parallelStream()
        .map(collectionName -> discoverFields(collectionName, mongoClient, databaseName, sampleSize))
        .filter(stream -> stream.isPresent())
        .map(stream -> stream.get())
        .collect(Collectors.toList());
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
  public static OptionalInt getDebeziumEventQueueSize(final MongoDbSourceConfig config) {
    final OptionalInt sizeFromConfig = config.getQueueSize();

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

  /**
   * Retrieves the statistics for the collection represented by the provided stream.
   *
   * @param mongoClient The {@link MongoClient} used to retrieve statistics from MongoDB.
   * @param stream The stream that represents the collection.
   * @return The {@link CollectionStatistics} of the collection or an empty {@link Optional} if the
   *         statistics cannot be retrieved.
   */
  public static Optional<CollectionStatistics> getCollectionStatistics(final MongoClient mongoClient, final ConfiguredAirbyteStream stream) {
    try {
      final Map<String, Object> collStats = Map.of(MongoConstants.STORAGE_STATS_KEY, Map.of(), MongoConstants.COUNT_KEY, Map.of());
      final MongoDatabase mongoDatabase = mongoClient.getDatabase(stream.getStream().getNamespace());
      final MongoCollection<Document> collection = mongoDatabase.getCollection(stream.getStream().getName());
      final AggregateIterable<Document> output = collection.aggregate(List.of(new Document("$collStats", collStats)));

      try (final MongoCursor<Document> cursor = output.allowDiskUse(true).cursor()) {
        if (cursor.hasNext()) {
          final Document stats = cursor.next();
          @SuppressWarnings("unchecked")
          final Map<String, Object> storageStats = (Map<String, Object>) stats.get(MongoConstants.STORAGE_STATS_KEY);
          if (storageStats != null && !storageStats.isEmpty()) {
            return Optional.of(new CollectionStatistics((Number) storageStats.get(MongoConstants.COLLECTION_STATISTICS_COUNT_KEY),
                (Number) storageStats.get(MongoConstants.COLLECTION_STATISTICS_STORAGE_SIZE_KEY)));
          } else {
            LOGGER.warn("Unable to estimate sync size:  statistics for {}.{} are missing.", stream.getStream().getNamespace(),
                stream.getStream().getName());
          }
        } else {
          LOGGER.warn("Unable to estimate sync size:  statistics for {}.{} are missing.", stream.getStream().getNamespace(),
              stream.getStream().getName());
        }
      }
    } catch (final Exception e) {
      LOGGER.warn("Error occurred while attempting to estimate sync size", e);
    }

    return Optional.empty();
  }

  /**
   * Creates an {@link AirbyteStream} from the provided data.
   *
   * @param collectionName The name of the collection represented by the stream (stream name).
   * @param databaseName The name of the database represented by the stream (stream namespace).
   * @param fields The fields available to the stream.
   * @return A {@link AirbyteStream} object representing the stream.
   */
  private static AirbyteStream createAirbyteStream(final String collectionName, final String databaseName, final List<Field> fields) {
    return MongoCatalogHelper.buildAirbyteStream(collectionName, databaseName, fields);
  }

  /**
   * Discovers the fields available to the stream.
   *
   * @param collectionName The name of the collection associated with the stream (stream name).
   * @param mongoClient The {@link MongoClient} used to access the fields.
   * @param databaseName The name of the database associated with the stream (stream namespace).
   * @param sampleSize The maximum number of documents to sample when attempting to discover the
   *        unique fields for a collection
   * @return The {@link AirbyteStream} that contains the discovered fields or an empty
   *         {@link Optional} if the underlying collection is empty.
   */
  private static Optional<AirbyteStream> discoverFields(final String collectionName,
                                                        final MongoClient mongoClient,
                                                        final String databaseName,
                                                        final Integer sampleSize) {
    /*
     * Fetch the keys/types from the first N documents and the last N documents from the collection.
     * This is an attempt to "survey" the documents in the collection for variance in the schema keys.
     */
    final MongoCollection<Document> mongoCollection = mongoClient.getDatabase(databaseName).getCollection(collectionName);
    final Set<Field> discoveredFields = new HashSet<>(getFieldsInCollection(mongoCollection, sampleSize));
    return Optional
        .ofNullable(!discoveredFields.isEmpty() ? createAirbyteStream(collectionName, databaseName, new ArrayList<>(discoveredFields)) : null);
  }

  private static Set<Field> getFieldsInCollection(final MongoCollection<Document> collection, final Integer sampleSize) {
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
    /*
     * Use sampling to reduce the time it takes to discover fields. Inspired by
     * https://www.mongodb.com/docs/compass/current/sampling/#sampling-method.
     */
    aggregateList.add(Aggregates.sample(sampleSize));
    aggregateList.add(Aggregates.project(new Document("fields", arrayToObjectAggregation)));
    aggregateList.add(Aggregates.unwind("$fields"));
    aggregateList.add(new Document("$group", groupMap));

    /*
     * Runs the following aggregation query: db.<collection name>.aggregate( [ { "$sample": { "size" :
     * 10000 } }, { "$project" : { "fields" : { "$arrayToObject": { "$map" : { "input" : {
     * "$objectToArray" : "$$ROOT" }, "as" : "each", "in" : { "k" : "$$each.k", "v" : { "$type" :
     * "$$each.v" } } } } } } }, { "$unwind" : "$fields" }, { "$group" : { "_id" : null, "fields" : {
     * "$addToSet" : "$fields" } } } ] )
     */
    final AggregateIterable<Document> output = collection.aggregate(aggregateList);

    try (final MongoCursor<Document> cursor = output.allowDiskUse(true).cursor()) {
      while (cursor.hasNext()) {
        @SuppressWarnings("unchecked")
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
      case "null" -> JsonSchemaType.NULL;
      default -> JsonSchemaType.STRING;
    };
  }

  private static boolean isSupportedCollection(final String collectionName) {
    return IGNORED_COLLECTIONS.stream().noneMatch(collectionName::startsWith);
  }

  /**
   * Represents statistics of a MongoDB collection.
   *
   * @param count The number of documents in the collection.
   * @param size The size (in bytes) of the collection.
   */
  public record CollectionStatistics(Number count, Number size) {}

}
