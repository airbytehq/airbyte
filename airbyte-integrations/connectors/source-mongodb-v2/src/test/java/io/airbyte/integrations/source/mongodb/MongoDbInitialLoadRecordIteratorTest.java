/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.mongodb.MongoException;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.exceptions.TransientErrorException;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import org.bson.Document;
import org.junit.jupiter.api.Test;

class MongoDbInitialLoadRecordIteratorTest {

  private static final AirbyteStreamNameNamespacePair STREAM =
      new AirbyteStreamNameNamespacePair("collection", "database");

  @Test
  void timeoutThrowsTransientErrorWithStreamName() {
    final MongoDbInitialLoadRecordIterator iterator = new MongoDbInitialLoadRecordIterator(
        mock(MongoCollection.class),
        new Document(),
        Optional.empty(),
        false,
        1,
        Instant.now().minusSeconds(1),
        Optional.of(Duration.ofMillis(1)),
        STREAM);

    final TransientErrorException exception = assertThrows(TransientErrorException.class, iterator::next);

    assertTrue(exception.getMessage().contains("collection"));
    assertFalse(exception.getCause() instanceof java.util.NoSuchElementException);
  }

  @Test
  void queryFailureAtChunkRolloverThrowsTransientError() {
    final MongoCollection<Document> collection = mock(MongoCollection.class);
    final FindIterable<Document> findIterable = mock(FindIterable.class);
    final MongoCursor<Document> firstCursor = mock(MongoCursor.class);
    when(collection.find()).thenReturn(findIterable);
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.limit(anyInt())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.allowDiskUse(anyBoolean())).thenReturn(findIterable);
    when(findIterable.cursor()).thenReturn(firstCursor).thenThrow(new MongoException("query failed"));
    when(firstCursor.hasNext()).thenReturn(true, false);
    when(firstCursor.next()).thenReturn(new Document("_id", "first"));

    final MongoDbInitialLoadRecordIterator iterator = new MongoDbInitialLoadRecordIterator(
        collection,
        new Document(),
        Optional.empty(),
        false,
        1,
        Instant.now(),
        Optional.empty(),
        STREAM);

    iterator.next();

    final TransientErrorException exception = assertThrows(TransientErrorException.class, iterator::hasNext);

    assertTrue(exception.getMessage().contains("database.collection"));
    assertTrue(exception.getInternalMessage().contains("query failed"));
  }

  @Test
  void emptyCollectionWithoutStateEndsCleanly() {
    final MongoCollection<Document> collection = mock(MongoCollection.class);
    final FindIterable<Document> findIterable = mock(FindIterable.class);
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    when(collection.find()).thenReturn(findIterable);
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.limit(anyInt())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.allowDiskUse(anyBoolean())).thenReturn(findIterable);
    when(findIterable.cursor()).thenReturn(cursor);
    when(cursor.hasNext()).thenReturn(false);

    final MongoDbInitialLoadRecordIterator iterator = new MongoDbInitialLoadRecordIterator(
        collection,
        new Document(),
        Optional.<MongoDbStreamState>empty(),
        false,
        1,
        Instant.now(),
        Optional.empty(),
        STREAM);

    assertFalse(iterator.hasNext());
  }

}
