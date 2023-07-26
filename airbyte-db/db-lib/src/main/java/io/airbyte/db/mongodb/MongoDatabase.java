/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.ConnectionString;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoConfigurationException;
import com.mongodb.ReadConcern;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoIterable;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.AbstractDatabase;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.bson.Document;
import org.bson.RawBsonDocument;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDatabase extends AbstractDatabase implements AutoCloseable {

  public static final String COLLECTION_COUNT_KEY = "collectionCount";
  public static final String COLLECTION_STORAGE_SIZE_KEY = "collectionStorageSize";

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDatabase.class);
  private static final int BATCH_SIZE = 1000;
  private static final String MONGO_RESERVED_COLLECTION_PREFIX = "system.";

  private final ConnectionString connectionString;
  private final com.mongodb.client.MongoDatabase database;
  private final MongoClient mongoClient;

  public MongoDatabase(final String connectionString, final String databaseName) {
    try {
      this.connectionString = new ConnectionString(connectionString);
      mongoClient = MongoClients.create(this.connectionString);
      database = mongoClient.getDatabase(databaseName);
    } catch (final MongoConfigurationException e) {
      LOGGER.error(e.getMessage(), e);
      throw new ConnectionErrorException(String.valueOf(e.getCode()), e.getMessage(), e);
    } catch (final Exception e) {
      LOGGER.error(e.getMessage(), e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    mongoClient.close();
  }

  public com.mongodb.client.MongoDatabase getDatabase() {
    return database;
  }

  public MongoIterable<String> getDatabaseNames() {
    return mongoClient.listDatabaseNames();
  }

  public Set<String> getCollectionNames() {
    final MongoIterable<String> collectionNames = database.listCollectionNames();
    if (collectionNames == null) {
      return Collections.EMPTY_SET;
    }
    return MoreIterators.toSet(database.listCollectionNames().iterator()).stream()
        .filter(c -> !c.startsWith(MONGO_RESERVED_COLLECTION_PREFIX)).collect(Collectors.toSet());
  }

  public MongoCollection<Document> getCollection(final String collectionName) {
    return database.getCollection(collectionName)
        .withReadConcern(ReadConcern.MAJORITY);
  }

  public MongoCollection<Document> getOrCreateNewCollection(final String collectionName) {
    final Set<String> collectionNames = MoreIterators.toSet(database.listCollectionNames().iterator());
    if (!collectionNames.contains(collectionName)) {
      database.createCollection(collectionName);
    }
    return database.getCollection(collectionName);
  }

  @VisibleForTesting
  public MongoCollection<Document> createCollection(final String name) {
    database.createCollection(name);
    return database.getCollection(name);
  }

  @VisibleForTesting
  public String getName() {
    return database.getName();
  }

  public Stream<JsonNode> read(final String collectionName, final List<String> columnNames, final Optional<Bson> filter) {
    try {
      final MongoCollection<RawBsonDocument> collection = database.getCollection(collectionName, RawBsonDocument.class);
      final MongoCursor<RawBsonDocument> cursor = collection
          .find(filter.orElse(new BsonDocument()))
          .batchSize(BATCH_SIZE)
          .cursor();

      return getStream(cursor, (document) -> MongoUtils.toJsonNode(document, columnNames))
          .onClose(() -> {
            try {
              cursor.close();
            } catch (final Exception e) {
              throw new RuntimeException(e.getMessage(), e);
            }
          });

    } catch (final Exception e) {
      LOGGER.error("Exception attempting to read data from collection: {}, {}", collectionName, e.getMessage());
      throw new RuntimeException(e);
    }
  }

  public Map<String, Object> getCollectionStats(final String collectionName) {
    try {
      final Document collectionStats = getDatabase().runCommand(new BsonDocument("collStats", new BsonString(collectionName)));
      final var count = collectionStats.get("count");
      final var storageSize = collectionStats.get("storageSize");

      if (count != null && storageSize != null) {
        return Map.of(COLLECTION_COUNT_KEY, collectionStats.get("count"),
            COLLECTION_STORAGE_SIZE_KEY, collectionStats.get("storageSize"));
      }
    } catch (final Exception e) {
      LOGGER.warn("Unable to retrieve collection statistics - {}", e.getMessage(), e);
    }

    return Map.of();
  }

  public String getServerType() {
    return mongoClient.getClusterDescription().getType().name();
  }

  public String getServerVersion() {
    try {
      return getDatabase().runCommand(new BsonDocument("buildinfo", new BsonString(""))).get("version").toString();
    } catch (final MongoCommandException e) {
      LOGGER.warn("Unable to retrieve server version", e);
      return null;
    }
  }

  private Stream<JsonNode> getStream(final MongoCursor<RawBsonDocument> cursor, final CheckedFunction<RawBsonDocument, JsonNode, Exception> mapper) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(final Consumer<? super JsonNode> action) {
        try {
          final RawBsonDocument document = cursor.tryNext();
          if (document == null) {
            return false;
          }
          action.accept(mapper.apply(document));
          return true;
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      }

    }, false);
  }

}
