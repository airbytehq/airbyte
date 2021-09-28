/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.ConnectionString;
import com.mongodb.ReadConcern;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoIterable;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.db.AbstractDatabase;
import java.util.List;
import java.util.Optional;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.function.Consumer;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.bson.BsonDocument;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDatabase extends AbstractDatabase {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDatabase.class);
  private static final int BATCH_SIZE = 1000;

  private final ConnectionString connectionString;
  private final String databaseName;

  private MongoClient mongoClient;

  public MongoDatabase(String uri, String databaseName) {
    try {
      connectionString = new ConnectionString(uri);
      mongoClient = MongoClients.create(connectionString);
      this.databaseName = databaseName;
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    mongoClient.close();
  }

  public com.mongodb.client.MongoDatabase getDatabase() {
    return mongoClient.getDatabase(databaseName);
  }

  public MongoIterable<String> getCollectionNames() {
    return getDatabase().listCollectionNames();
  }

  public MongoCollection<Document> getCollection(String collectionName) {
    return getDatabase().getCollection(collectionName)
        .withReadConcern(ReadConcern.MAJORITY);
  }

  @VisibleForTesting
  public MongoCollection<Document> createCollection(String name) {
    getDatabase().createCollection(name);
    return getDatabase().getCollection(name);
  }

  @VisibleForTesting
  public String getName() {
    return getDatabase().getName();
  }

  public Stream<JsonNode> read(String collectionName, List<String> columnNames, Optional<Bson> filter) {
    try {
      final MongoCollection<Document> collection = getDatabase().getCollection(collectionName);
      final MongoCursor<Document> cursor = collection
          .find(filter.orElse(new BsonDocument()))
          .batchSize(BATCH_SIZE)
          .cursor();

      return getStream(cursor, (document) -> MongoUtils.toJsonNode(document, columnNames))
          .onClose(() -> {
            try {
              cursor.close();
            } catch (Exception e) {
              throw new RuntimeException();
            }
          });

    } catch (Exception e) {
      LOGGER.error("Exception attempting to read data from collection: ", collectionName, e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private Stream<JsonNode> getStream(MongoCursor<Document> cursor, CheckedFunction<Document, JsonNode, Exception> mapper) {
    return StreamSupport.stream(new Spliterators.AbstractSpliterator<>(Long.MAX_VALUE, Spliterator.ORDERED) {

      @Override
      public boolean tryAdvance(Consumer<? super JsonNode> action) {
        try {
          Document document = cursor.tryNext();
          if (document == null) {
            return false;
          }
          action.accept(mapper.apply(document));
          return true;
        } catch (Exception e) {
          throw new RuntimeException(e);
        }
      }

    }, false);
  }

}
