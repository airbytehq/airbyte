/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.state.IdType.idToStringRepresenation;
import static io.airbyte.integrations.source.mongodb.state.IdType.parseBinaryIdString;
import static io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus.IN_PROGRESS;

import com.google.common.collect.AbstractIterator;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Sorts;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import java.util.Optional;
import org.bson.*;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This record iterator operates over a single stream. It continuously reads data from a table via
 * multiple queries with the configured chunk size until the entire table is processed. The next
 * query uses the highest watermark of the primary key seen in the previous subquery.
 */
public class MongoDbInitialLoadRecordIterator extends AbstractIterator<Document>
    implements AutoCloseableIterator<Document> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbInitialLoadRecordIterator.class);
  private final boolean isEnforceSchema;
  private final MongoCollection<Document> collection;
  private final Bson fields;
  // Represents the number of rows to get with each query.
  private final int chunkSize;

  private Optional<MongoDbStreamState> currentState;
  private MongoCursor<Document> currentIterator;

  private int numSubqueries = 0;

  MongoDbInitialLoadRecordIterator(final MongoCollection<Document> collection,
                                   final Bson fields,
                                   final Optional<MongoDbStreamState> existingState,
                                   final boolean isEnforceSchema,
                                   final int chunkSize) {
    this.collection = collection;
    this.fields = fields;
    this.currentState = existingState;
    this.isEnforceSchema = isEnforceSchema;
    this.chunkSize = chunkSize;
    this.currentIterator = buildNewQueryIterator();
  }

  @Override
  protected Document computeNext() {
    if (shouldBuildNextQuery()) {
      try {
        LOGGER.info("Finishing subquery number : {}, processing at id : {}", numSubqueries,
            currentState.get() == null ? "starting null" : currentState.get().id());
        currentIterator.close();
        currentIterator = buildNewQueryIterator();
        numSubqueries++;
        if (!currentIterator.hasNext()) {
          return endOfData();
        }
      } catch (final Exception e) {
        return endOfData();
      }
    }
    // Get the new _id field to start the next subquery from.
    Document next = currentIterator.next();
    currentState = getCurrentState(next.get(MongoConstants.ID_FIELD));
    return next;
  }

  private Optional<MongoDbStreamState> getCurrentState(Object currentId) {
    final var idType = IdType.findByJavaType(currentId.getClass().getSimpleName())
        .orElseThrow(() -> new ConfigErrorException("Unsupported _id type " + currentId.getClass().getSimpleName()));

    final var state = new MongoDbStreamState(idToStringRepresenation(currentId, idType),
        IN_PROGRESS,
        idType);
    return Optional.of(state);
  }

  @Override
  public void close() throws Exception {
    if (currentIterator != null) {
      currentIterator.close();
    }
  }

  private MongoCursor<Document> buildNewQueryIterator() {
    Bson filter = buildFilter();
    return isEnforceSchema ? collection.find()
        .filter(filter)
        .projection(fields)
        .limit(chunkSize)
        .sort(Sorts.ascending(MongoConstants.ID_FIELD))
        .allowDiskUse(true)
        .cursor()
        : collection.find()
            .filter(filter)
            .limit(chunkSize)
            .sort(Sorts.ascending(MongoConstants.ID_FIELD))
            .allowDiskUse(true)
            .cursor();
  }

  private Bson buildFilter() {
    // The filter determines the starting point of this iterator based on the state of this collection.
    // If a state exists, it will use that state to create a query akin to
    // "where _id > [last saved state] order by _id ASC".
    // If no state exists, it will create a query akin to "where 1=1 order by _id ASC"
    return currentState
        // Full refresh streams that finished set their id to null
        // This tells us to start over
        .filter(state -> state.id() != null)
        .map(state -> Filters.gt(MongoConstants.ID_FIELD,
            switch (state.idType()) {
            case STRING -> new BsonString(state.id());
            case OBJECT_ID -> new BsonObjectId(new ObjectId(state.id()));
            case INT -> new BsonInt32(Integer.parseInt(state.id()));
            case LONG -> new BsonInt64(Long.parseLong(state.id()));
            case BINARY -> parseBinaryIdString(state.id());
            }))
        // if nothing was found, return a new BsonDocument
        .orElseGet(BsonDocument::new);
  }

  private boolean shouldBuildNextQuery() {
    // The next sub-query should be built if the previous subquery has finished.
    return !currentIterator.hasNext();
  }

}
